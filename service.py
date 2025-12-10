"""
语音识别服务 - 支持说话人分离和语音转文字
包含任务上传和结果查询API
"""
import os
import uuid
import json
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict
import sqlite3
from contextlib import contextmanager

# 加载环境变量
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # python-dotenv 是可选的

import torch
import torchaudio
from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from pyannote.audio import Pipeline
from transformers import (
    AutoConfig,
    AutoModelForCausalLM,
    AutoTokenizer,
    WhisperFeatureExtractor,
)

from inference import build_prompt, prepare_inputs, WHISPER_FEAT_CFG

# 配置
UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR", "./uploads"))
CHECKPOINT_DIR = Path(os.getenv("CHECKPOINT_DIR", Path(__file__).parent))
DB_PATH = os.getenv("DB_PATH", "tasks.db")
DEVICE = os.getenv("DEVICE", "cuda" if torch.cuda.is_available() else "cpu")
SERVICE_HOST = os.getenv("SERVICE_HOST", "0.0.0.0")
SERVICE_PORT = int(os.getenv("SERVICE_PORT", "6006"))

# 确保上传目录存在
UPLOAD_DIR.mkdir(exist_ok=True)

app = FastAPI(title="语音识别服务", description="支持说话人分离的语音转文字服务")


# ==================== 数据库模型 ====================

class TaskStatus:
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


@contextmanager
def get_db():
    """数据库连接上下文管理器"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db():
    """初始化数据库"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                task_id TEXT PRIMARY KEY,
                filename TEXT NOT NULL,
                file_path TEXT NOT NULL,
                status TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                error_message TEXT,
                result TEXT
            )
        """)


# ==================== API 模型 ====================

class TaskResponse(BaseModel):
    task_id: str
    status: str
    message: str


class Speaker(BaseModel):
    speaker_id: str
    start: float
    end: float
    text: str


class TaskResult(BaseModel):
    task_id: str
    status: str
    filename: str
    created_at: str
    updated_at: str
    error_message: Optional[str] = None
    speakers: Optional[List[Speaker]] = None


# ==================== 全局模型加载 ====================

class ModelManager:
    """模型管理器 - 单例模式"""
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self.tokenizer = None
        self.feature_extractor = None
        self.asr_model = None
        self.diarization_pipeline = None
        self._initialized = True
    
    def load_asr_model(self):
        """加载ASR模型"""
        if self.asr_model is not None:
            return
        
        print("Loading ASR model...")
        self.tokenizer = AutoTokenizer.from_pretrained(CHECKPOINT_DIR)
        self.feature_extractor = WhisperFeatureExtractor(**WHISPER_FEAT_CFG)
        
        config = AutoConfig.from_pretrained(CHECKPOINT_DIR, trust_remote_code=True)
        self.asr_model = AutoModelForCausalLM.from_pretrained(
            CHECKPOINT_DIR,
            config=config,
            torch_dtype=torch.bfloat16,
            trust_remote_code=True,
        ).to(DEVICE)
        self.asr_model.eval()
        print("ASR model loaded successfully")
    
    def load_diarization_pipeline(self, use_auth_token: Optional[str] = None):
        """加载说话人分离模型"""
        if self.diarization_pipeline is not None:
            return
        
        print("Loading diarization pipeline...")
        # 需要 Hugging Face token 来访问 pyannote 模型
        # 可以从环境变量获取: export HUGGINGFACE_TOKEN=your_token
        token = use_auth_token or os.getenv("HUGGINGFACE_TOKEN")
        if not token:
            raise ValueError(
                "需要 Hugging Face token 来访问 pyannote 模型。"
                "请设置环境变量 HUGGINGFACE_TOKEN 或在初始化时传入。"
                "获取token: https://huggingface.co/settings/tokens"
            )
        
        self.diarization_pipeline = Pipeline.from_pretrained(
            "pyannote/speaker-diarization-3.1",
            use_auth_token=token
        )
        
        if torch.cuda.is_available():
            self.diarization_pipeline.to(torch.device(DEVICE))
        
        print("Diarization pipeline loaded successfully")


model_manager = ModelManager()


# ==================== 核心处理函数 ====================

def diarize_audio(audio_path: Path) -> List[Dict]:
    """
    使用 pyannote-audio 进行说话人分离
    返回: [{"speaker": "SPEAKER_00", "start": 0.0, "end": 5.0}, ...]
    """
    model_manager.load_diarization_pipeline()
    
    diarization = model_manager.diarization_pipeline(str(audio_path))
    
    segments = []
    for turn, _, speaker in diarization.itertracks(yield_label=True):
        segments.append({
            "speaker": speaker,
            "start": turn.start,
            "end": turn.end
        })
    
    return segments


def extract_audio_segment(audio_path: Path, start: float, end: float) -> torch.Tensor:
    """提取音频片段"""
    wav, sr = torchaudio.load(str(audio_path))
    wav = wav[:1, :]  # 转单声道
    
    # 转换为正确的采样率
    if sr != 16000:
        wav = torchaudio.transforms.Resample(sr, 16000)(wav)
        sr = 16000
    
    # 提取片段
    start_sample = int(start * sr)
    end_sample = int(end * sr)
    segment = wav[:, start_sample:end_sample]
    
    return segment, sr


def transcribe_segment(audio_segment: torch.Tensor, sr: int) -> str:
    """转录音频片段"""
    model_manager.load_asr_model()
    
    # 保存临时音频文件
    temp_path = UPLOAD_DIR / f"temp_{uuid.uuid4()}.wav"
    torchaudio.save(str(temp_path), audio_segment, sr)
    
    try:
        batch = build_prompt(
            temp_path,
            model_manager.tokenizer,
            model_manager.feature_extractor,
            merge_factor=model_manager.asr_model.config.merge_factor,
        )
        
        model_inputs, prompt_len = prepare_inputs(batch, DEVICE)
        
        with torch.inference_mode():
            generated = model_manager.asr_model.generate(
                **model_inputs,
                max_new_tokens=256,
                do_sample=False,
            )
        
        transcript_ids = generated[0, prompt_len:].cpu().tolist()
        transcript = model_manager.tokenizer.decode(
            transcript_ids, skip_special_tokens=True
        ).strip()
        
        return transcript or "[Empty]"
    
    finally:
        # 清理临时文件
        if temp_path.exists():
            temp_path.unlink()


def process_audio_task(task_id: str):
    """处理音频任务的主函数"""
    try:
        # 更新任务状态为处理中
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE tasks SET status = ?, updated_at = ? WHERE task_id = ?",
                (TaskStatus.PROCESSING, datetime.now().isoformat(), task_id)
            )
            
            # 获取任务信息
            cursor.execute("SELECT file_path FROM tasks WHERE task_id = ?", (task_id,))
            row = cursor.fetchone()
            if not row:
                raise ValueError(f"Task {task_id} not found")
            
            file_path = Path(row["file_path"])
        
        # 步骤1: 说话人分离
        print(f"Task {task_id}: Starting speaker diarization...")
        diarization_segments = diarize_audio(file_path)
        print(f"Task {task_id}: Found {len(diarization_segments)} speaker segments")
        
        # 步骤2: 对每个片段进行语音识别
        results = []
        for i, segment in enumerate(diarization_segments):
            print(f"Task {task_id}: Transcribing segment {i+1}/{len(diarization_segments)}")
            
            # 提取音频片段
            audio_segment, sr = extract_audio_segment(
                file_path,
                segment["start"],
                segment["end"]
            )
            
            # 转录
            text = transcribe_segment(audio_segment, sr)
            
            results.append({
                "speaker_id": segment["speaker"],
                "start": segment["start"],
                "end": segment["end"],
                "text": text
            })
        
        # 步骤3: 保存结果
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """UPDATE tasks 
                   SET status = ?, updated_at = ?, result = ? 
                   WHERE task_id = ?""",
                (
                    TaskStatus.COMPLETED,
                    datetime.now().isoformat(),
                    json.dumps(results, ensure_ascii=False),
                    task_id
                )
            )
        
        print(f"Task {task_id}: Completed successfully")
    
    except Exception as e:
        print(f"Task {task_id}: Failed with error: {str(e)}")
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """UPDATE tasks 
                   SET status = ?, updated_at = ?, error_message = ? 
                   WHERE task_id = ?""",
                (
                    TaskStatus.FAILED,
                    datetime.now().isoformat(),
                    str(e),
                    task_id
                )
            )


# ==================== API 端点 ====================

@app.on_event("startup")
async def startup_event():
    """应用启动时初始化"""
    init_db()
    print("Database initialized")
    print(f"Service running on device: {DEVICE}")


@app.post("/api/tasks/upload", response_model=TaskResponse)
async def upload_audio_task(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(..., description="音频文件 (支持 wav, mp3, m4a 等格式)")
):
    """
    上传音频文件创建转录任务
    
    - **file**: 音频文件
    
    返回任务ID，可用于查询结果
    """
    # 验证文件类型
    if not file.filename:
        raise HTTPException(status_code=400, detail="无效的文件")
    
    allowed_extensions = {".wav", ".mp3", ".m4a", ".flac", ".ogg", ".aac"}
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"不支持的文件格式。支持的格式: {', '.join(allowed_extensions)}"
        )
    
    # 生成任务ID
    task_id = str(uuid.uuid4())
    
    # 保存文件
    file_path = UPLOAD_DIR / f"{task_id}{file_ext}"
    try:
        content = await file.read()
        with open(file_path, "wb") as f:
            f.write(content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"文件保存失败: {str(e)}")
    
    # 创建任务记录
    now = datetime.now().isoformat()
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO tasks 
               (task_id, filename, file_path, status, created_at, updated_at)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (task_id, file.filename, str(file_path), TaskStatus.PENDING, now, now)
        )
    
    # 添加后台任务处理
    background_tasks.add_task(process_audio_task, task_id)
    
    return TaskResponse(
        task_id=task_id,
        status=TaskStatus.PENDING,
        message="任务已创建，正在处理中"
    )


@app.get("/api/tasks/{task_id}", response_model=TaskResult)
async def get_task_result(task_id: str):
    """
    查询任务结果
    
    - **task_id**: 任务ID
    
    返回任务状态和转录结果（如果已完成）
    """
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM tasks WHERE task_id = ?", (task_id,))
        row = cursor.fetchone()
    
    if not row:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    result = {
        "task_id": row["task_id"],
        "status": row["status"],
        "filename": row["filename"],
        "created_at": row["created_at"],
        "updated_at": row["updated_at"],
        "error_message": row["error_message"]
    }
    
    # 如果任务完成，解析结果
    if row["status"] == TaskStatus.COMPLETED and row["result"]:
        speakers_data = json.loads(row["result"])
        result["speakers"] = [
            Speaker(
                speaker_id=s["speaker_id"],
                start=s["start"],
                end=s["end"],
                text=s["text"]
            )
            for s in speakers_data
        ]
    else:
        result["speakers"] = None
    
    return TaskResult(**result)


@app.get("/api/tasks")
async def list_tasks(
    status: Optional[str] = None,
    limit: int = 100,
    offset: int = 0
):
    """
    列出所有任务
    
    - **status**: 过滤状态 (可选: pending, processing, completed, failed)
    - **limit**: 返回数量限制
    - **offset**: 偏移量
    """
    with get_db() as conn:
        cursor = conn.cursor()
        
        if status:
            query = """
                SELECT task_id, filename, status, created_at, updated_at 
                FROM tasks 
                WHERE status = ?
                ORDER BY created_at DESC
                LIMIT ? OFFSET ?
            """
            cursor.execute(query, (status, limit, offset))
        else:
            query = """
                SELECT task_id, filename, status, created_at, updated_at 
                FROM tasks 
                ORDER BY created_at DESC
                LIMIT ? OFFSET ?
            """
            cursor.execute(query, (limit, offset))
        
        rows = cursor.fetchall()
        
        return {
            "tasks": [
                {
                    "task_id": row["task_id"],
                    "filename": row["filename"],
                    "status": row["status"],
                    "created_at": row["created_at"],
                    "updated_at": row["updated_at"]
                }
                for row in rows
            ],
            "count": len(rows)
        }


@app.get("/")
async def root():
    """服务健康检查"""
    return {
        "service": "语音识别服务",
        "status": "running",
        "device": DEVICE,
        "endpoints": {
            "upload": "/api/tasks/upload",
            "get_result": "/api/tasks/{task_id}",
            "list_tasks": "/api/tasks"
        }
    }


if __name__ == "__main__":
    import uvicorn
    
    # 运行服务
    uvicorn.run(
        app,
        host=SERVICE_HOST,
        port=SERVICE_PORT,
        log_level="info"
    )
