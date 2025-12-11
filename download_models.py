#!/usr/bin/env python3
"""
模型下载脚本
提前下载 pyannote-audio 模型，避免首次运行时等待
"""
import os
import sys
from pathlib import Path

def check_token():
    """检查 Hugging Face Token"""
    token = os.getenv("HUGGINGFACE_TOKEN")
    
    if not token:
        print("❌ 错误: 未设置 HUGGINGFACE_TOKEN 环境变量")
        print("\n请按以下步骤操作:")
        print("1. 访问 https://huggingface.co/settings/tokens")
        print("2. 创建新的 token (Read 权限)")
        print("3. 接受模型使用条款:")
        print("   - https://huggingface.co/pyannote/speaker-diarization-3.1")
        print("   - https://huggingface.co/pyannote/segmentation-3.0")
        print("\n4. 设置环境变量:")
        print("   export HUGGINGFACE_TOKEN=your_token_here")
        print("\n或者在 .env 文件中设置")
        return False
    
    print(f"✓ 检测到 HUGGINGFACE_TOKEN: {token[:10]}...{token[-4:]}")
    return True


def check_huggingface_cli():
    """检查 huggingface-cli 是否安装"""
    import subprocess
    try:
        result = subprocess.run(
            ["huggingface-cli", "--version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            return True
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
    return False


def download_pyannote_models():
    """使用 huggingface-cli 下载 pyannote 模型"""
    print("\n" + "="*60)
    print("开始下载 pyannote-audio 模型")
    print("="*60)
    
    # 检查 huggingface-cli
    if not check_huggingface_cli():
        print("\n❌ 未找到 huggingface-cli")
        print("请先安装:")
        print("   pip install -U huggingface_hub[cli]")
        return False
    
    import subprocess
    
    # 先登录
    token = os.getenv("HUGGINGFACE_TOKEN")
    print("\n🔐 使用 Token 登录 Hugging Face...")
    try:
        result = subprocess.run(
            ["huggingface-cli", "login", "--token", token],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            print("✓ 登录成功")
        else:
            print(f"⚠️  登录警告: {result.stderr}")
    except Exception as e:
        print(f"⚠️  登录失败: {str(e)}")
        print("继续尝试下载...")
    
    # 模型列表
    models = [
        "pyannote/speaker-diarization-3.1",
        "pyannote/segmentation-3.0",
    ]
    
    success = True
    for model_name in models:
        print(f"\n📦 下载模型: {model_name}")
        print("   这可能需要几分钟时间，请耐心等待...")
        
        try:
            # 使用 huggingface-cli 下载
            result = subprocess.run(
                ["huggingface-cli", "download", model_name],
                capture_output=False,  # 显示下载进度
                text=True,
                timeout=600  # 10分钟超时
            )
            
            if result.returncode == 0:
                print(f"   ✓ {model_name} 下载完成")
            else:
                print(f"   ✗ {model_name} 下载失败")
                success = False
                
        except subprocess.TimeoutExpired:
            print(f"   ✗ {model_name} 下载超时")
            success = False
        except Exception as e:
            print(f"   ✗ {model_name} 下载失败: {str(e)}")
            success = False
    
    if success:
        print("\n" + "="*60)
        print("✅ 所有 pyannote 模型下载完成！")
        print("="*60)
    else:
        print("\n" + "="*60)
        print("⚠️  部分模型下载失败")
        print("="*60)
    
    return success


def check_glm_asr_model():
    """检查 GLM-ASR 模型"""
    print("\n" + "="*60)
    print("检查 GLM-ASR 模型")
    print("="*60)
    
    required_files = [
        "config.json",
        "generation_config.json",
        "tokenizer_config.json",
    ]
    
    missing = []
    for filename in required_files:
        if Path(filename).exists():
            print(f"✓ {filename}")
        else:
            print(f"✗ {filename} (缺失)")
            missing.append(filename)
    
    if missing:
        print("\n⚠️  GLM-ASR 模型文件不完整")
        print("\n请下载模型:")
        print("   方式1: Git LFS")
        print("   git lfs install")
        print("   git clone https://huggingface.co/zai-org/GLM-ASR-Nano-2512")
        print("\n   方式2: 使用 huggingface_hub")
        print("   pip install huggingface_hub")
        print("   python -c \"from huggingface_hub import snapshot_download; snapshot_download('zai-org/GLM-ASR-Nano-2512', local_dir='.')\"")
        return False
    else:
        print("\n✅ GLM-ASR 模型文件完整")
        return True


def test_imports():
    """测试关键导入"""
    print("\n" + "="*60)
    print("测试依赖包")
    print("="*60)
    
    packages = {
        "torch": "PyTorch",
        "torchaudio": "TorchAudio",
        "transformers": "Transformers",
        "pyannote.audio": "Pyannote Audio",
        "fastapi": "FastAPI",
        "uvicorn": "Uvicorn",
    }
    
    all_ok = True
    for package, name in packages.items():
        try:
            __import__(package)
            print(f"✓ {name}")
        except ImportError:
            print(f"✗ {name} (未安装)")
            all_ok = False
    
    if not all_ok:
        print("\n请安装缺失的包:")
        print("   pip install -r requirements.txt")
        return False
    
    print("\n✅ 所有依赖包已安装")
    return True


def show_cache_info():
    """显示缓存信息"""
    print("\n" + "="*60)
    print("缓存位置")
    print("="*60)
    
    # Hugging Face 缓存
    hf_cache = os.getenv("HF_HOME", os.path.expanduser("~/.cache/huggingface"))
    print(f"📁 Hugging Face 缓存: {hf_cache}")
    
    # Transformers 缓存
    transformers_cache = os.getenv("TRANSFORMERS_CACHE", os.path.expanduser("~/.cache/huggingface/transformers"))
    print(f"📁 Transformers 缓存: {transformers_cache}")
    
    # PyTorch 缓存
    torch_cache = os.getenv("TORCH_HOME", os.path.expanduser("~/.cache/torch"))
    print(f"📁 PyTorch 缓存: {torch_cache}")
    
    print("\n💡 提示: 如需清理缓存，可以删除上述目录")


def main():
    """主函数"""
    print("="*60)
    print("GLM-ASR 服务 - 模型下载工具")
    print("="*60)
    
    # 加载 .env 文件（如果存在）
    try:
        from dotenv import load_dotenv
        if Path(".env").exists():
            load_dotenv()
            print("✓ 已加载 .env 文件")
    except ImportError:
        pass
    
    # 步骤1: 检查 Token
    if not check_token():
        return 1
    
    # 步骤2: 测试依赖
    if not test_imports():
        return 1
    
    # 步骤3: 检查 GLM-ASR 模型
    check_glm_asr_model()
    
    # 步骤4: 下载 pyannote 模型
    print("\n是否下载 pyannote 模型? (这需要几分钟时间)")
    response = input("继续? [Y/n]: ").strip().lower()
    
    if response in ['', 'y', 'yes']:
        if not download_pyannote_models():
            return 1
    else:
        print("跳过模型下载")
    
    # 步骤5: 显示缓存信息
    show_cache_info()
    
    print("\n" + "="*60)
    print("✨ 设置完成！")
    print("="*60)
    print("\n现在可以启动服务:")
    print("   python service.py")
    print("   # 或")
    print("   ./start_service.sh")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
