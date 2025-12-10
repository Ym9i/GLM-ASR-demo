#!/bin/bash

# 语音识别服务快速启动脚本

echo "================================="
echo "语音识别服务启动脚本"
echo "================================="
echo ""

# 检查 Python
if ! command -v python3 &> /dev/null; then
    echo "错误: 未找到 Python3"
    exit 1
fi

echo "✓ Python3 版本: $(python3 --version)"

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo ""
    echo "创建虚拟环境..."
    python3 -m venv venv
    echo "✓ 虚拟环境已创建"
fi

# 激活虚拟环境
echo ""
echo "激活虚拟环境..."
source venv/bin/activate
echo "✓ 虚拟环境已激活"

# 安装依赖
echo ""
echo "检查依赖..."
pip install -q --upgrade pip
pip install -q -r requirements.txt
echo "✓ 依赖已安装"

# 检查环境变量
if [ ! -f ".env" ]; then
    echo ""
    echo "警告: 未找到 .env 文件"
    echo "请确保设置了 HUGGINGFACE_TOKEN 环境变量"
    echo "或者从 .env.example 创建 .env 文件"
    echo ""
    
    if [ -z "$HUGGINGFACE_TOKEN" ]; then
        echo "当前未设置 HUGGINGFACE_TOKEN 环境变量"
        echo ""
        read -p "是否继续启动? (y/n) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    else
        echo "✓ 检测到 HUGGINGFACE_TOKEN 环境变量"
    fi
else
    echo "✓ 找到 .env 文件"
    set -a
    source .env
    set +a
fi

# 启动服务
echo ""
echo "================================="
echo "启动服务..."
echo "================================="
echo ""
echo "服务地址: http://localhost:6006"
echo "API 文档: http://localhost:6006/docs"
echo ""
echo "按 Ctrl+C 停止服务"
echo ""

python3 service.py
