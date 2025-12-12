#!/usr/bin/env python3
"""
使用 pyannote-audio 进行说话人分段
需要 Hugging Face token 才能使用预训练模型
"""

from pyannote.audio import Pipeline
import torch
import os
from dotenv import load_dotenv

# 加载 .env 文件
load_dotenv()

# 音频文件路径
audio_file = "202512101639.wav"

# 从环境变量中读取 Hugging Face token
hf_token = os.getenv("HF_TOKEN")
if not hf_token:
    raise ValueError("请在 .env 文件中设置 HF_TOKEN")

# 加载预训练的说话人分段模型
# 注意：首次使用需要在 https://huggingface.co/pyannote/speaker-diarization 接受用户协议
print(f"正在加载模型...")
pipeline = Pipeline.from_pretrained(
    "pyannote/speaker-diarization-3.1",
    use_auth_token=hf_token
)

# 如果有 GPU，使用 GPU 加速
if torch.cuda.is_available():
    pipeline.to(torch.device("cuda"))

# 执行说话人分段
print(f"正在处理音频文件: {audio_file}")
diarization = pipeline(audio_file)

# 打印结果
print("\n说话人分段结果:")
print("=" * 60)
for turn, _, speaker in diarization.itertracks(yield_label=True):
    print(f"说话人 {speaker}: {turn.start:.2f}秒 -> {turn.end:.2f}秒 (时长: {turn.end - turn.start:.2f}秒)")

# 保存结果到文件
output_file = "diarization_result.txt"
with open(output_file, "w", encoding="utf-8") as f:
    f.write("说话人分段结果\n")
    f.write("=" * 60 + "\n\n")
    for turn, _, speaker in diarization.itertracks(yield_label=True):
        f.write(f"说话人 {speaker}: {turn.start:.2f}秒 -> {turn.end:.2f}秒 (时长: {turn.end - turn.start:.2f}秒)\n")

print(f"\n结果已保存到: {output_file}")

# 保存为 RTTM 格式（标准的说话人分段格式）
rttm_file = "diarization_result.rttm"
with open(rttm_file, "w") as f:
    diarization.write_rttm(f)
print(f"RTTM 格式结果已保存到: {rttm_file}")

# 统计信息
speakers = set()
for turn, _, speaker in diarization.itertracks(yield_label=True):
    speakers.add(speaker)

print(f"\n统计信息:")
print(f"检测到 {len(speakers)} 个说话人: {', '.join(sorted(speakers))}")
