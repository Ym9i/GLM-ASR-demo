#!/usr/bin/env python3
"""
环境验证脚本 - 检查所有依赖和配置
"""
import sys
import os
from pathlib import Path

def print_status(message, status="info"):
    """打印带颜色的状态信息"""
    colors = {
        "success": "\033[92m",  # 绿色
        "error": "\033[91m",    # 红色
        "warning": "\033[93m",  # 黄色
        "info": "\033[94m",     # 蓝色
        "reset": "\033[0m"
    }
    
    symbols = {
        "success": "✓",
        "error": "✗",
        "warning": "⚠",
        "info": "ℹ"
    }
    
    color = colors.get(status, colors["info"])
    symbol = symbols.get(status, "•")
    reset = colors["reset"]
    
    print(f"{color}{symbol} {message}{reset}")


def check_python_version():
    """检查 Python 版本"""
    print("\n1. 检查 Python 版本...")
    version = sys.version_info
    
    if version >= (3, 8):
        print_status(f"Python {version.major}.{version.minor}.{version.micro}", "success")
        return True
    else:
        print_status(f"Python 版本过低 ({version.major}.{version.minor}), 需要 >= 3.8", "error")
        return False


def check_packages():
    """检查必需的 Python 包"""
    print("\n2. 检查 Python 包...")
    
    required_packages = {
        "torch": "PyTorch",
        "torchaudio": "TorchAudio",
        "transformers": "Transformers",
        "fastapi": "FastAPI",
        "uvicorn": "Uvicorn",
        "pyannote.audio": "Pyannote Audio",
    }
    
    all_installed = True
    
    for package, name in required_packages.items():
        try:
            if package == "pyannote.audio":
                __import__("pyannote.audio")
            else:
                __import__(package)
            print_status(f"{name} 已安装", "success")
        except ImportError:
            print_status(f"{name} 未安装", "error")
            all_installed = False
    
    return all_installed


def check_gpu():
    """检查 GPU 支持"""
    print("\n3. 检查 GPU 支持...")
    
    try:
        import torch
        
        if torch.cuda.is_available():
            gpu_count = torch.cuda.device_count()
            gpu_name = torch.cuda.get_device_name(0)
            print_status(f"CUDA 可用: {gpu_count} 个 GPU", "success")
            print_status(f"GPU 0: {gpu_name}", "info")
            return True
        else:
            print_status("CUDA 不可用，将使用 CPU", "warning")
            return False
    except Exception as e:
        print_status(f"无法检查 GPU: {e}", "warning")
        return False


def check_env_variables():
    """检查环境变量"""
    print("\n4. 检查环境变量...")
    
    token = os.getenv("HUGGINGFACE_TOKEN")
    
    if token:
        print_status("HUGGINGFACE_TOKEN 已设置", "success")
        print_status(f"Token: {token[:10]}...{token[-4:]}", "info")
        return True
    else:
        print_status("HUGGINGFACE_TOKEN 未设置", "warning")
        print_status("pyannote 模型需要此 token", "info")
        
        # 检查 .env 文件
        if Path(".env").exists():
            print_status("找到 .env 文件", "info")
        else:
            print_status("未找到 .env 文件", "warning")
            print_status("建议从 .env.example 创建 .env 文件", "info")
        
        return False


def check_files():
    """检查必需的文件"""
    print("\n5. 检查项目文件...")
    
    required_files = {
        "service.py": "主服务文件",
        "inference.py": "推理模块",
        "requirements.txt": "依赖文件",
        "test_service.py": "测试脚本",
    }
    
    all_exist = True
    
    for filename, description in required_files.items():
        if Path(filename).exists():
            print_status(f"{description} ({filename})", "success")
        else:
            print_status(f"{description} ({filename}) 不存在", "error")
            all_exist = False
    
    return all_exist


def check_directories():
    """检查和创建必需的目录"""
    print("\n6. 检查目录结构...")
    
    directories = {
        "uploads": "上传文件目录",
    }
    
    for dirname, description in directories.items():
        dir_path = Path(dirname)
        if dir_path.exists():
            print_status(f"{description} ({dirname})", "success")
        else:
            print_status(f"{description} ({dirname}) 不存在，正在创建...", "warning")
            dir_path.mkdir(parents=True, exist_ok=True)
            print_status(f"已创建 {dirname}", "success")
    
    return True


def test_imports():
    """测试关键导入"""
    print("\n7. 测试关键功能...")
    
    tests = [
        ("import torch", "PyTorch"),
        ("import torchaudio", "TorchAudio"),
        ("import transformers", "Transformers"),
        ("import fastapi", "FastAPI"),
        ("from pyannote.audio import Pipeline", "Pyannote Pipeline"),
    ]
    
    all_passed = True
    
    for code, name in tests:
        try:
            exec(code)
            print_status(f"{name} 导入测试", "success")
        except Exception as e:
            print_status(f"{name} 导入失败: {str(e)[:50]}", "error")
            all_passed = False
    
    return all_passed


def check_model_files():
    """检查模型文件"""
    print("\n8. 检查模型文件...")
    
    model_files = [
        "config.json",
        "generation_config.json",
        "tokenizer_config.json",
    ]
    
    found = 0
    for filename in model_files:
        if Path(filename).exists():
            found += 1
    
    if found == len(model_files):
        print_status("所有模型配置文件存在", "success")
        return True
    elif found > 0:
        print_status(f"找到 {found}/{len(model_files)} 个模型文件", "warning")
        print_status("请确保 GLM-ASR 模型文件完整", "info")
        return False
    else:
        print_status("未找到模型文件", "error")
        print_status("请下载 GLM-ASR 模型", "info")
        return False


def main():
    """主函数"""
    print("=" * 60)
    print("语音识别服务 - 环境验证")
    print("=" * 60)
    
    results = {
        "Python 版本": check_python_version(),
        "Python 包": check_packages(),
        "GPU 支持": check_gpu(),
        "环境变量": check_env_variables(),
        "项目文件": check_files(),
        "目录结构": check_directories(),
        "功能测试": test_imports(),
        "模型文件": check_model_files(),
    }
    
    # 总结
    print("\n" + "=" * 60)
    print("验证总结")
    print("=" * 60)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for name, result in results.items():
        status = "success" if result else "error"
        print_status(f"{name}: {'通过' if result else '失败'}", status)
    
    print(f"\n通过: {passed}/{total}")
    
    if passed == total:
        print_status("\n✨ 所有检查通过！可以启动服务。", "success")
        print("\n启动命令:")
        print("  python service.py")
        print("  # 或")
        print("  ./start_service.sh")
        return 0
    else:
        print_status("\n⚠️  部分检查未通过，请查看上述信息。", "warning")
        print("\n建议操作:")
        
        if not results["Python 包"]:
            print("  1. 安装依赖: pip install -r requirements.txt")
        
        if not results["环境变量"]:
            print("  2. 设置环境变量:")
            print("     export HUGGINGFACE_TOKEN=your_token")
            print("     # 或创建 .env 文件")
        
        if not results["模型文件"]:
            print("  3. 下载模型:")
            print("     git lfs clone https://huggingface.co/zai-org/GLM-ASR-Nano-2512")
        
        return 1


if __name__ == "__main__":
    sys.exit(main())
