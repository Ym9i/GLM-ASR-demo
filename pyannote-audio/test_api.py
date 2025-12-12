#!/usr/bin/env python3
"""测试 pyannote API 使用"""

from pyannote.audio import Pipeline
import torch
import os
from dotenv import load_dotenv

load_dotenv()

audio_file = "202512101639_16k.wav"
hf_token = os.getenv("HF_TOKEN")

print("加载模型...")
pipeline = Pipeline.from_pretrained("pyannote/speaker-diarization-3.1", token=hf_token)
pipeline.to(torch.device("cpu"))

print("处理音频...")
diarization = pipeline(audio_file, min_speakers=1, max_speakers=5)

print(f"\n返回类型: {type(diarization)}")
print(f"可用方法: {[m for m in dir(diarization) if not m.startswith('_')]}")

print("\n说话人分段结果:")
print("=" * 60)

# 正确的迭代方式: DiarizeOutput.speaker_diarization 才是 Annotation 对象
for turn, _, speaker in diarization.speaker_diarization.itertracks(yield_label=True):
    print(f"说话人 {speaker}: {turn.start:.2f}秒 -> {turn.end:.2f}秒")

print("\n✓ 测试成功!")
