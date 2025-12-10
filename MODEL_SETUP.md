# 模型准备指南

本文档说明如何提前下载和准备服务所需的模型。

## 为什么要提前下载模型？

1. **避免首次运行时长时间等待** - pyannote 模型约 1GB，下载需要几分钟
2. **验证环境配置** - 提前发现配置问题
3. **离线部署** - 可以在有网络的环境下载，然后部署到无网络环境

## 所需模型

### 1. GLM-ASR 模型（语音识别）

**模型**: zai-org/GLM-ASR-Nano-2512

**下载方式**:

#### 方式 A: Git LFS（推荐）
```bash
git lfs install
git clone https://huggingface.co/zai-org/GLM-ASR-Nano-2512
cd GLM-ASR-Nano-2512
# 将所有文件复制到项目根目录
```

#### 方式 B: 使用 huggingface_hub
```bash
pip install huggingface_hub
python -c "from huggingface_hub import snapshot_download; snapshot_download('zai-org/GLM-ASR-Nano-2512', local_dir='.')"
```

### 2. pyannote-audio 模型（说话人分离）

**模型**: 
- pyannote/speaker-diarization-3.1
- pyannote/segmentation-3.0

**前提条件**:
1. 获取 Hugging Face Token: https://huggingface.co/settings/tokens
2. 接受模型使用条款:
   - https://huggingface.co/pyannote/speaker-diarization-3.1
   - https://huggingface.co/pyannote/segmentation-3.0

**下载方式**:

使用提供的自动化脚本：

```bash
# 设置 Token
export HUGGINGFACE_TOKEN=your_token_here

# 运行下载脚本
python download_models.py
```

## 使用模型下载脚本

我们提供了 `download_models.py` 脚本来自动化整个过程。

### 功能

✅ 检查 HUGGINGFACE_TOKEN 配置  
✅ 验证所有依赖包安装情况  
✅ 检查 GLM-ASR 模型文件  
✅ 自动下载 pyannote-audio 模型  
✅ 显示模型缓存位置  

### 使用步骤

1. **设置环境变量**
```bash
export HUGGINGFACE_TOKEN=your_token_here
```

2. **运行下载脚本**
```bash
python download_models.py
```

3. **按提示操作**
```
是否下载 pyannote 模型? (这需要几分钟时间)
继续? [Y/n]: y
```

### 输出示例

```
============================================================
GLM-ASR 服务 - 模型下载工具
============================================================
✓ 检测到 HUGGINGFACE_TOKEN: hf_xxxxxx...xxxx

============================================================
测试依赖包
============================================================
✓ PyTorch
✓ TorchAudio
✓ Transformers
✓ Pyannote Audio
✓ FastAPI
✓ Uvicorn

✅ 所有依赖包已安装

============================================================
检查 GLM-ASR 模型
============================================================
✓ config.json
✓ generation_config.json
✓ tokenizer_config.json

✅ GLM-ASR 模型文件完整

============================================================
开始下载 pyannote-audio 模型
============================================================

📦 下载模型: pyannote/speaker-diarization-3.1
   这可能需要几分钟时间，请耐心等待...
   ✓ pyannote/speaker-diarization-3.1 下载完成

📦 下载模型: pyannote/segmentation-3.0
   这可能需要几分钟时间，请耐心等待...
   ✓ pyannote/segmentation-3.0 下载完成

============================================================
✅ 所有 pyannote 模型下载完成！
============================================================

============================================================
缓存位置
============================================================
📁 Hugging Face 缓存: ~/.cache/huggingface
📁 Transformers 缓存: ~/.cache/huggingface/transformers
📁 PyTorch 缓存: ~/.cache/torch

💡 提示: 如需清理缓存，可以删除上述目录

============================================================
✨ 设置完成！
============================================================

现在可以启动服务:
   python service.py
   # 或
   ./start_service.sh
```

## 模型存储位置

### 默认缓存位置

- **Linux/macOS**: `~/.cache/huggingface/`
- **Windows**: `C:\Users\<username>\.cache\huggingface\`

### 自定义缓存位置

可以通过环境变量指定：

```bash
export HF_HOME=/path/to/custom/cache
export TRANSFORMERS_CACHE=/path/to/custom/cache/transformers
```

## 离线部署

如果需要在无网络环境部署：

1. **在有网络的机器上下载模型**
```bash
python download_models.py
```

2. **打包缓存目录**
```bash
tar -czf models_cache.tar.gz ~/.cache/huggingface
```

3. **在目标机器上解压**
```bash
tar -xzf models_cache.tar.gz -C ~/
```

4. **启动服务**（无需网络）
```bash
python service.py
```

## 验证模型

下载完成后，可以使用验证脚本检查：

```bash
python verify_setup.py
```

这将检查：
- Python 版本
- 依赖包
- 环境变量
- 模型文件
- GPU 支持

## 常见问题

### Q: 下载速度很慢怎么办？

A: 可以使用镜像站点：
```bash
# 使用国内镜像
export HF_ENDPOINT=https://hf-mirror.com
python download_models.py
```

### Q: 提示 Token 无效？

A: 确认：
1. Token 是否正确复制（没有多余空格）
2. 是否接受了模型使用条款
3. Token 是否有 Read 权限

### Q: 下载中断了怎么办？

A: 重新运行脚本，会自动续传：
```bash
python download_models.py
```

### Q: 如何查看已下载的模型？

A: 查看缓存目录：
```bash
ls -lh ~/.cache/huggingface/hub/
```

### Q: 磁盘空间不足？

A: 模型大小约：
- GLM-ASR: ~3GB
- pyannote-audio: ~1GB
- 总计: ~4GB

确保有足够空间。

## 手动下载（高级）

如果自动脚本不工作，可以手动下载：

### 下载 pyannote 模型

```python
from pyannote.audio import Pipeline
import os

os.environ["HUGGINGFACE_TOKEN"] = "your_token_here"

# 下载模型
pipeline = Pipeline.from_pretrained(
    "pyannote/speaker-diarization-3.1",
    use_auth_token=os.environ["HUGGINGFACE_TOKEN"]
)
print("✓ speaker-diarization-3.1 下载完成")

pipeline = Pipeline.from_pretrained(
    "pyannote/segmentation-3.0",
    use_auth_token=os.environ["HUGGINGFACE_TOKEN"]
)
print("✓ segmentation-3.0 下载完成")
```

## 下一步

模型准备完成后：

1. **验证环境**: `python verify_setup.py`
2. **启动服务**: `python service.py`
3. **测试服务**: `python test_service.py your_audio.wav`

更多信息请查看：
- [快速开始指南](QUICKSTART.md)
- [服务使用文档](SERVICE_README.md)
