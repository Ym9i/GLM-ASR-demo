#!/usr/bin/env python3
"""
优化版说话人分段脚本 - 适用于内存有限的环境
通过分段处理和内存优化来处理大音频文件
"""

from pyannote.audio import Pipeline
import torch
import os
from dotenv import load_dotenv
import gc
from pydub import AudioSegment
import tempfile

# 加载 .env 文件
load_dotenv()

# 音频文件路径
audio_file = "202512101639.wav"

# 从环境变量中读取 Hugging Face token
hf_token = os.getenv("HF_TOKEN")
if not hf_token:
    raise ValueError("请在 .env 文件中设置 HF_TOKEN")

# 配置参数
CHUNK_DURATION_MINUTES = 5  # 每次处理5分钟的音频
OVERLAP_SECONDS = 30  # 重叠30秒以避免边界问题

def get_audio_duration(audio_path):
    """获取音频时长(秒)"""
    audio = AudioSegment.from_wav(audio_path)
    return len(audio) / 1000.0

def split_audio(audio_path, chunk_duration_ms, overlap_ms):
    """将音频分割成小块"""
    audio = AudioSegment.from_wav(audio_path)
    chunks = []
    
    start = 0
    while start < len(audio):
        end = min(start + chunk_duration_ms, len(audio))
        chunk = audio[start:end]
        chunks.append((start / 1000.0, chunk))  # 返回开始时间(秒)和音频块
        start += chunk_duration_ms - overlap_ms
        
        if start >= len(audio):
            break
    
    return chunks

def process_audio_in_chunks(audio_file, pipeline):
    """分块处理音频文件"""
    duration = get_audio_duration(audio_file)
    print(f"音频总时长: {duration:.2f} 秒 ({duration/60:.2f} 分钟)")
    
    # 如果音频较短,直接处理
    if duration < CHUNK_DURATION_MINUTES * 60:
        print("音频较短,直接处理...")
        return pipeline(audio_file, min_speakers=1, max_speakers=5)
    
    # 分块处理
    print(f"音频较长,将分为 {CHUNK_DURATION_MINUTES} 分钟的块进行处理...")
    chunk_duration_ms = CHUNK_DURATION_MINUTES * 60 * 1000
    overlap_ms = OVERLAP_SECONDS * 1000
    
    chunks = split_audio(audio_file, chunk_duration_ms, overlap_ms)
    print(f"共分为 {len(chunks)} 个块")
    
    all_results = []
    
    for i, (start_time, chunk) in enumerate(chunks):
        print(f"\n处理块 {i+1}/{len(chunks)} (起始时间: {start_time:.2f}秒)...")
        
        # 保存临时音频文件
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_file:
            chunk.export(tmp_file.name, format="wav")
            tmp_path = tmp_file.name
        
        try:
            # 处理这一块
            diarization = pipeline(tmp_path, min_speakers=1, max_speakers=5)
            
            # 调整时间戳 (使用 .speaker_diarization 获取 Annotation 对象)
            for turn, _, speaker in diarization.speaker_diarization.itertracks(yield_label=True):
                adjusted_start = turn.start + start_time
                adjusted_end = turn.end + start_time
                all_results.append((adjusted_start, adjusted_end, speaker))
            
            # 清理内存
            del diarization
            gc.collect()
            
        finally:
            # 删除临时文件
            os.unlink(tmp_path)
    
    return all_results

# 加载模型
print("正在加载模型...")
pipeline = Pipeline.from_pretrained(
    "pyannote/speaker-diarization-3.1",
    token=hf_token
)

# 使用 CPU(更稳定,内存使用可控)
device = torch.device("cpu")
pipeline.to(device)
print("使用 CPU 进行处理(内存优化模式)")

# 执行说话人分段
print(f"\n正在处理音频文件: {audio_file}")
results = process_audio_in_chunks(audio_file, pipeline)

# 处理结果
if isinstance(results, list):
    # 分块处理的结果
    print("\n说话人分段结果:")
    print("=" * 60)
    for start, end, speaker in sorted(results, key=lambda x: x[0]):
        print(f"说话人 {speaker}: {start:.2f}秒 -> {end:.2f}秒 (时长: {end - start:.2f}秒)")
    
    # 保存结果
    output_file = "diarization_result.txt"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("说话人分段结果\n")
        f.write("=" * 60 + "\n\n")
        for start, end, speaker in sorted(results, key=lambda x: x[0]):
            f.write(f"说话人 {speaker}: {start:.2f}秒 -> {end:.2f}秒 (时长: {end - start:.2f}秒)\n")
    
    # 统计信息
    speakers = set(speaker for _, _, speaker in results)
    print(f"\n统计信息:")
    print(f"检测到 {len(speakers)} 个说话人: {', '.join(sorted(speakers))}")
    
else:
    # 直接处理的结果 (DiarizeOutput 对象)
    print("\n说话人分段结果:")
    print("=" * 60)
    
    # 收集所有结果用于显示和保存
    all_segments = []
    speakers = set()
    
    # DiarizeOutput.speaker_diarization 是 Annotation 对象,才有 itertracks 方法
    for turn, _, speaker in results.speaker_diarization.itertracks(yield_label=True):
        all_segments.append((turn.start, turn.end, speaker))
        speakers.add(speaker)
        print(f"说话人 {speaker}: {turn.start:.2f}秒 -> {turn.end:.2f}秒 (时长: {turn.end - turn.start:.2f}秒)")
    
    # 保存结果
    output_file = "diarization_result.txt"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("说话人分段结果\n")
        f.write("=" * 60 + "\n\n")
        for start, end, speaker in all_segments:
            f.write(f"说话人 {speaker}: {start:.2f}秒 -> {end:.2f}秒 (时长: {end - start:.2f}秒)\n")
    
    # 保存为 RTTM 格式
    rttm_file = "diarization_result.rttm"
    with open(rttm_file, "w") as f:
        results.speaker_diarization.write_rttm(f)
    print(f"RTTM 格式结果已保存到: {rttm_file}")
    
    # 统计信息
    print(f"\n统计信息:")
    print(f"检测到 {len(speakers)} 个说话人: {', '.join(sorted(speakers))}")

print(f"结果已保存到: {output_file}")
