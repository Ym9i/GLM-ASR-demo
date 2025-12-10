# 项目总结 - 语音识别服务

## 📋 项目概述

基于 GLM-ASR 和 pyannote-audio 构建的完整语音识别服务，支持说话人分离和语音转文字功能。

## 🎯 核心功能

1. **说话人分离** - 使用 pyannote-audio 自动识别音频中的不同说话人
2. **语音转文字** - 使用 GLM-ASR 将每个说话人的语音转换为文字
3. **异步任务处理** - 后台处理长音频，避免阻塞
4. **任务管理** - 使用 SQLite 存储和管理任务状态
5. **RESTful API** - 提供标准的 HTTP API 接口

## 📁 文件结构

```
GLM-ASR-demo/
├── service.py              # 主服务文件（FastAPI 应用）
├── test_service.py         # 测试客户端脚本
├── inference.py            # 原始 ASR 推理代码
├── download_models.py      # 模型下载工具
├── requirements.txt        # Python 依赖
│
├── SERVICE_README.md       # 详细使用文档
├── QUICKSTART.md          # 快速开始指南
├── PROJECT_SUMMARY.md     # 本文件
│
├── start_service.sh       # 启动脚本（Linux/macOS）
├── .env.example           # 环境变量示例
├── Dockerfile            # Docker 镜像配置
├── docker-compose.yml    # Docker Compose 配置
│
├── web_ui.html           # 简单的 Web 界面
│
├── uploads/              # 上传文件存储目录（自动创建）
└── tasks.db              # SQLite 数据库（自动创建）
```

## 🔧 技术栈

- **Web 框架**: FastAPI + Uvicorn
- **语音识别**: GLM-ASR (Transformers)
- **说话人分离**: pyannote-audio
- **数据库**: SQLite
- **深度学习**: PyTorch, torchaudio

## 🚀 API 端点

### 1. 上传任务
- **端点**: `POST /api/tasks/upload`
- **功能**: 上传音频文件，创建转录任务
- **返回**: 任务 ID

### 2. 查询结果
- **端点**: `GET /api/tasks/{task_id}`
- **功能**: 查询任务状态和结果
- **返回**: 任务详情和转录结果

### 3. 列出任务
- **端点**: `GET /api/tasks`
- **功能**: 列出所有任务（支持过滤和分页）
- **返回**: 任务列表

### 4. 健康检查
- **端点**: `GET /`
- **功能**: 检查服务状态
- **返回**: 服务信息

## 🔄 工作流程

```
用户上传音频
    ↓
创建任务记录（status: pending）
    ↓
后台任务开始处理（status: processing）
    ├─ 步骤1: 说话人分离（pyannote-audio）
    │   └─ 输出: [(speaker, start, end), ...]
    ├─ 步骤2: 提取音频片段
    │   └─ 为每个说话人片段提取音频
    └─ 步骤3: 语音转文字（GLM-ASR）
        └─ 对每个片段进行转录
    ↓
保存结果（status: completed）
    ↓
用户查询并获取结果
```

## 📊 数据库结构

### tasks 表
```sql
CREATE TABLE tasks (
    task_id TEXT PRIMARY KEY,        -- 任务唯一ID
    filename TEXT NOT NULL,          -- 原始文件名
    file_path TEXT NOT NULL,         -- 服务器文件路径
    status TEXT NOT NULL,            -- 任务状态
    created_at TEXT NOT NULL,        -- 创建时间
    updated_at TEXT NOT NULL,        -- 更新时间
    error_message TEXT,              -- 错误信息
    result TEXT                      -- JSON格式结果
);
```

## 🎨 使用示例

### Python 客户端
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
result = requests.get(
    f"http://localhost:6006/api/tasks/{task_id}"
).json()
```

### 命令行
```bash
# 使用测试脚本
python test_service.py audio.wav

# 使用 curl
curl -X POST "http://localhost:6006/api/tasks/upload" \
  -F "file=@audio.wav"
```

### Web 界面
```bash
# 在浏览器中打开
open web_ui.html
# 或使用服务器
python -m http.server 8080
```

## ⚙️ 配置选项

环境变量（可通过 .env 文件设置）：

```bash
HUGGINGFACE_TOKEN=xxx       # Hugging Face token（必需）
SERVICE_HOST=0.0.0.0        # 服务地址
SERVICE_PORT=6006           # 服务端口
DEVICE=cuda                 # 计算设备（cuda/cpu）
CHECKPOINT_DIR=./           # 模型目录
UPLOAD_DIR=./uploads        # 上传文件目录
DB_PATH=./tasks.db          # 数据库路径
```

## 📈 性能考虑

### GPU vs CPU
- **GPU**: 推荐用于生产环境，处理速度快 5-10 倍
- **CPU**: 适合开发测试，但处理较慢

### 内存需求
- **说话人分离**: ~2GB
- **ASR 模型**: ~3GB
- **音频处理**: 根据音频长度动态分配

### 处理时间（参考）
- 1 分钟音频（GPU）: ~30 秒
- 1 分钟音频（CPU）: ~3-5 分钟

## 🔒 安全建议

1. **生产环境**:
   - 添加用户认证（JWT）
   - 限制上传文件大小
   - 使用 HTTPS
   - 设置速率限制

2. **文件管理**:
   - 定期清理旧文件
   - 实现文件过期机制
   - 添加病毒扫描

3. **数据库**:
   - 定期备份
   - 考虑迁移到 PostgreSQL（大规模）

## 🚧 已知限制

1. **并发处理**: 当前版本串行处理任务，建议使用 Celery 实现分布式处理
2. **长音频**: 超过 30 分钟的音频可能导致内存问题
3. **实时性**: 不支持实时流式处理
4. **多语言**: 当前主要支持中文，其他语言需要调整

## 🔮 未来改进

### 短期
- [ ] WebSocket 支持（实时进度推送）
- [ ] 批量上传
- [ ] 导出多种格式（SRT, DOCX, PDF）
- [ ] 音频预处理（降噪、归一化）

### 中期
- [ ] 用户认证和权限管理
- [ ] 多语言支持
- [ ] 说话人识别（识别特定人物）
- [ ] 任务优先级和队列管理

### 长期
- [ ] 实时流式处理
- [ ] 云存储集成（S3, OSS）
- [ ] 分布式处理（Celery, RabbitMQ）
- [ ] 微服务架构

## 📚 相关资源

- **GLM-ASR**: https://huggingface.co/zai-org/GLM-ASR-Nano-2512
- **pyannote-audio**: https://github.com/pyannote/pyannote-audio
- **FastAPI**: https://fastapi.tiangolo.com/
- **PyTorch**: https://pytorch.org/

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

请遵循 GLM-ASR 和 pyannote-audio 的相关许可证。

---

**创建日期**: 2025-12-10
**版本**: 1.0.0
