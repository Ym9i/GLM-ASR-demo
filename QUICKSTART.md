# 快速开始指南

## 1. 准备工作

### 1.1 获取 Hugging Face Token

1. 访问 https://huggingface.co/settings/tokens
2. 点击 "New token"
3. 输入名称（如 "pyannote-access"），选择 "Read" 权限
4. 复制生成的 token

### 1.2 接受模型使用条款（必须！）

⚠️ **这是最重要的步骤，不完成会提示无权访问！**

1. 登录 Hugging Face 账号
2. 访问以下链接，点击页面上的 **"Agree and access repository"** 按钮：
   - https://huggingface.co/pyannote/speaker-diarization-3.1
   - https://huggingface.co/pyannote/segmentation-3.0
3. 等待几秒钟，权限会自动生效

## 2. 安装

### 方式 1: 本地安装（推荐开发使用）

```bash
# 克隆或下载项目
cd GLM-ASR-demo

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 设置环境变量
export HUGGINGFACE_TOKEN=your_token_here

# 提前下载模型（推荐）
python download_models.py
```

### 方式 2: 使用启动脚本（最简单）

```bash
# 设置环境变量
export HUGGINGFACE_TOKEN=your_token_here

# 启动服务（会自动安装依赖）
chmod +x start_service.sh
./start_service.sh
```

**注意**: 首次运行时，服务会自动下载 pyannote 模型（约 1GB），可能需要几分钟。如果想提前下载，可以先运行 `python download_models.py`。

## 3. 启动服务

```bash
# 确保已设置 HUGGINGFACE_TOKEN
export HUGGINGFACE_TOKEN=your_token_here

# 启动服务
python service.py
```

服务将在 http://localhost:6006 启动

## 4. 测试服务

### 4.1 访问 API 文档

打开浏览器访问：http://localhost:6006/docs

### 4.2 使用测试脚本

```bash
# 上传音频并等待结果
python test_service.py your_audio.wav

# 列出所有任务
python test_service.py list

# 查询特定任务
python test_service.py get <task_id>
```

### 4.3 使用 curl

```bash
# 上传音频文件
curl -X POST "http://localhost:6006/api/tasks/upload" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@test_audio.wav"

# 返回示例:
# {"task_id":"123e4567-e89b-12d3-a456-426614174000","status":"pending","message":"任务已创建，正在处理中"}

# 查询结果
curl "http://localhost:6006/api/tasks/123e4567-e89b-12d3-a456-426614174000"
```

### 4.4 使用 Python

```python
import requests

# 上传文件
with open("audio.wav", "rb") as f:
    response = requests.post(
        "http://localhost:6006/api/tasks/upload",
        files={"file": f}
    )
    task_id = response.json()["task_id"]

# 查询结果
result = requests.get(f"http://localhost:6006/api/tasks/{task_id}").json()
print(result)
```

## 5. 工作流程

```
1. 用户上传音频文件
   ↓
2. 服务返回 task_id
   ↓
3. 后台处理开始:
   - 说话人分离 (pyannote-audio)
   - 按说话人片段提取音频
   - 语音转文字 (GLM-ASR)
   ↓
4. 用户轮询查询任务状态
   ↓
5. 任务完成，返回结果:
   - 每个说话人的时间段
   - 对应的文字转录
```

## 6. 结果格式

```json
{
  "task_id": "123e4567-e89b-12d3-a456-426614174000",
  "status": "completed",
  "filename": "meeting.wav",
  "created_at": "2025-12-10T10:00:00",
  "updated_at": "2025-12-10T10:05:30",
  "speakers": [
    {
      "speaker_id": "SPEAKER_00",
      "start": 0.0,
      "end": 5.3,
      "text": "大家好，今天我们讨论一下项目进展。"
    },
    {
      "speaker_id": "SPEAKER_01",
      "start": 5.5,
      "end": 10.2,
      "text": "好的，我先说一下我这边的情况。"
    },
    {
      "speaker_id": "SPEAKER_00",
      "start": 10.5,
      "end": 15.8,
      "text": "请讲。"
    }
  ]
}
```

## 7. 常见问题

### Q: 首次运行很慢？
A: 首次运行会下载 pyannote 模型（约 1GB），请耐心等待。

### Q: 内存不足？
A: 尝试处理较短的音频，或使用 CPU 模式（虽然较慢）。

### Q: CUDA 错误？
A: 检查 PyTorch 和 CUDA 版本是否匹配，或设置 `export DEVICE=cpu` 使用 CPU。

### Q: Token 无效？
A: 确认已接受 pyannote 模型的使用条款。

### Q: 任务一直 pending？
A: 查看服务器日志，可能是模型加载失败或内存不足。

## 8. 性能优化

- **使用 GPU**: 显著提升处理速度（5-10倍）
- **音频预处理**: 转换为 16kHz 单声道 WAV 格式
- **批量处理**: 将长音频分段处理
- **缓存模型**: 首次加载后模型会保持在内存中

## 9. 下一步

- 查看 `SERVICE_README.md` 了解详细文档
- 查看 `test_service.py` 了解客户端使用示例
- 查看 API 文档: http://localhost:6006/docs

## 10. 获取帮助

- 查看日志文件
- 查看任务的 `error_message` 字段
- 提交 Issue 到 GitHub
