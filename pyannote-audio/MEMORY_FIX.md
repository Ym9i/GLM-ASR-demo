# 内存不足问题解决方案

## 问题原因
`Killed` 错误表示程序被系统终止,通常是由于内存不足(OOM)导致的。pyannote-audio 在处理大音频文件时需要大量内存。

## 解决方案

### 方案1: 使用优化版脚本(推荐)
我已创建了 `speaker_diarization_optimized.py`,它会自动分块处理大音频文件:

```bash
# 先安装额外依赖
pip install pydub

# 运行优化版脚本
python speaker_diarization_optimized.py
```

这个脚本会:
- 自动检测音频长度
- 将长音频分成5分钟的小块
- 逐块处理以减少内存使用
- 自动合并结果

### 方案2: 手动分割音频文件
使用 ffmpeg 将音频分割成更小的片段:

```bash
# 安装 ffmpeg (如果未安装)
brew install ffmpeg

# 分割音频为5分钟的片段
ffmpeg -i 202512101639.wav -f segment -segment_time 300 -c copy output_%03d.wav

# 分别处理每个片段
python speaker_diarization.py  # 修改音频文件名
```

### 方案3: 降低音频质量
降低采样率和比特率以减少内存使用:

```bash
# 降低采样率到16kHz(语音识别的标准采样率)
ffmpeg -i 202512101639.wav -ar 16000 202512101639_16k.wav

# 然后处理降采样后的文件
python speaker_diarization.py  # 修改音频文件名
```

### 方案4: 限制说话人数量
原始脚本已更新,添加了 `max_speakers=5` 参数来限制最大说话人数量,这可以减少计算量。

### 方案5: 增加系统交换空间(临时方案)
如果您在 Linux/macOS 上运行,可以临时增加交换空间:

**macOS:**
```bash
# macOS 会自动管理交换空间,但可以检查可用内存
vm_stat
```

**Linux:**
```bash
# 创建交换文件(例如 8GB)
sudo fallocate -l 8G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

## 推荐做法

1. **首选**: 使用 `speaker_diarization_optimized.py` (已自动优化)
2. 如果仍然失败,先用 ffmpeg 降低采样率到 16kHz
3. 如果音频超过30分钟,考虑手动分割

## 内存使用估算

- 短音频(<5分钟): 约 2-4GB RAM
- 中等音频(5-15分钟): 约 4-8GB RAM  
- 长音频(>15分钟): 约 8-16GB RAM

## 其他优化建议

1. 关闭其他占用内存的程序
2. 确保使用 CPU 模式(更稳定,内存可控)
3. 考虑使用云服务器(如有更大内存需求)
