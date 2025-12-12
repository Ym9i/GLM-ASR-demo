# 说话人分段 (Speaker Diarization)

使用 pyannote-audio 对音频文件进行说话人分段分析。

## 安装依赖

```bash
pip install pyannote.audio
```

## 配置 Hugging Face Token

1. 访问 https://huggingface.co/settings/tokens
2. 创建一个新的 access token
3. 访问 https://huggingface.co/pyannote/speaker-diarization-3.1 并接受用户协议
4. 访问 https://huggingface.co/pyannote/segmentation-3.0 并接受用户协议
5. 在 `speaker_diarization.py` 中替换 `YOUR_HF_TOKEN_HERE` 为你的实际 token

## 使用方法

```bash
python speaker_diarization.py
```

## 输出

- `diarization_result.txt`: 易读的文本格式结果
- `diarization_result.rttm`: 标准的 RTTM 格式结果

## 结果格式

```
说话人 SPEAKER_00: 0.50秒 -> 5.23秒 (时长: 4.73秒)
说话人 SPEAKER_01: 5.80秒 -> 10.15秒 (时长: 4.35秒)
...
```
