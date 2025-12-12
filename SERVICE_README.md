# 语音识别服务使用说明

## 功能概述

这是一个基于 GLM-ASR 和 pyannote-audio 的语音识别服务，支持以下功能：

1. **说话人分离 (Speaker Diarization)**: 自动识别音频中不同的说话人
2. **语音转文字 (ASR)**: 将每个说话人的语音转换为文字
3. **异步任务处理**: 支持上传任务后台处理，避免长时间等待
4. **任务查询**: 可随时查询任务状态和结果
5. **SQLite 存储**: 所有任务和结果都存储在本地数据库中

## 安装依赖

### 1. 安装 Python 依赖

```bash
pip install -r requirements.txt
```

### 2. 获取 Hugging Face Token

pyannote-audio 模型需要 Hugging Face token 才能使用：

1. 访问 https://huggingface.co/settings/tokens
2. 创建一个新的 token (Read 权限即可)
3. 接受 pyannote 模型的使用条款：
   - 访问 https://huggingface.co/pyannote/speaker-diarization-3.1
   - 点击 "Agree and access repository"

### 3. 设置环境变量

```bash
export HUGGINGFACE_TOKEN=your_token_here
```

或者在 `.env` 文件中设置：

```
HUGGINGFACE_TOKEN=your_token_here
```

### 4. 下载模型（可选但推荐）

提前下载模型可以避免首次运行时等待：

```bash
python download_models.py
```

这个脚本会：
- 检查依赖包安装情况
- 验证 HUGGINGFACE_TOKEN
- 下载 pyannote-audio 模型（约 1GB）
- 检查 GLM-ASR 模型文件

## 启动服务

```bash
python service.py
```

服务将在 `http://localhost:6006` 启动。

您可以访问 `http://localhost:6006/docs` 查看自动生成的 API 文档。

**注意**: 首次运行时，如果未提前下载模型，服务启动时会自动下载 pyannote 模型，这可能需要几分钟时间。建议使用 `python download_models.py` 提前下载。

## API 使用

### 1. 上传音频文件（创建任务）

**端点**: `POST /api/tasks/upload`

**请求**:
```bash
curl -X POST "http://localhost:6006/api/tasks/upload" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@your_audio.wav"
```

**响应**:
```json
{
  "task_id": "123e4567-e89b-12d3-a456-426614174000",
  "status": "pending",
  "message": "任务已创建，正在处理中"
}
```

支持的音频格式：`.wav`, `.mp3`, `.m4a`, `.flac`, `.ogg`, `.aac`

### 2. 查询任务结果

**端点**: `GET /api/tasks/{task_id}`

**请求**:
```bash
curl -X GET "http://localhost:6006/api/tasks/123e4567-e89b-12d3-a456-426614174000"
```

**响应（处理中）**:
```json
{
  "task_id": "123e4567-e89b-12d3-a456-426614174000",
  "status": "processing",
  "filename": "your_audio.wav",
  "created_at": "2025-12-10T10:30:00",
  "updated_at": "2025-12-10T10:30:05",
  "error_message": null,
  "speakers": null
}
```

**响应（已完成）**:
```json
{
  "task_id": "123e4567-e89b-12d3-a456-426614174000",
  "status": "completed",
  "filename": "your_audio.wav",
  "created_at": "2025-12-10T10:30:00",
  "updated_at": "2025-12-10T10:31:30",
  "error_message": null,
  "speakers": [
    {
      "speaker_id": "SPEAKER_00",
      "start": 0.0,
      "end": 5.3,
      "text": "你好，很高兴见到你。"
    },
    {
      "speaker_id": "SPEAKER_01",
      "start": 5.5,
      "end": 8.9,
      "text": "我也很高兴见到你，今天天气真好。"
    },
    {
      "speaker_id": "SPEAKER_00",
      "start": 9.0,
      "end": 12.5,
      "text": "是啊，我们去散步吧。"
    }
  ]
}
```

### 3. 列出所有任务

**端点**: `GET /api/tasks`

**请求**:
```bash
# 获取所有任务
curl -X GET "http://localhost:6006/api/tasks"

# 只获取已完成的任务
curl -X GET "http://localhost:6006/api/tasks?status=completed"

# 分页
curl -X GET "http://localhost:6006/api/tasks?limit=10&offset=0"
```

**响应**:
```json
{
  "tasks": [
    {
      "task_id": "123e4567-e89b-12d3-a456-426614174000",
      "filename": "audio1.wav",
      "status": "completed",
      "created_at": "2025-12-10T10:30:00",
      "updated_at": "2025-12-10T10:31:30"
    }
  ],
  "count": 1
}
```

## 任务状态说明

- `pending`: 任务已创建，等待处理
- `processing`: 任务正在处理中
- `completed`: 任务已完成
- `failed`: 任务失败（查看 `error_message` 了解详情）

## 数据库

任务数据存储在 `tasks.db` SQLite 数据库中，包含以下字段：

- `task_id`: 任务唯一标识符
- `filename`: 原始文件名
- `file_path`: 服务器上的文件路径
- `status`: 任务状态
- `created_at`: 创建时间
- `updated_at`: 更新时间
- `error_message`: 错误信息（如果失败）
- `result`: JSON 格式的结果数据

## 文件存储

上传的音频文件存储在 `./uploads` 目录中，文件名为 `{task_id}{原始扩展名}`。

## Python 客户端示例

参考 `test_service.py` 文件中的示例代码。

## 注意事项

1. **模型下载**: 首次运行时会自动下载 pyannote 模型，可能需要一些时间
2. **GPU 支持**: 如果有 CUDA 支持的 GPU，服务会自动使用 GPU 加速
3. **内存需求**: 处理长音频文件可能需要较多内存
4. **并发处理**: 当前版本使用后台任务串行处理，生产环境建议使用 Celery 等任务队列
5. **文件清理**: 服务不会自动删除上传的文件，需要定期清理 `./uploads` 目录

## 性能优化建议

1. 对于长音频（>30分钟），建议先分割再处理
2. 使用 GPU 可以显著提升处理速度
3. 可以调整 `max_new_tokens` 参数来控制转录长度
4. 考虑使用 Redis 作为任务队列，支持分布式处理

## 故障排查

### 问题：pyannote 模型加载失败或提示 "Access restricted"

⚠️ **这是最常见的问题！**

**错误信息**:
```
Cannot access gated repo for url https://huggingface.co/pyannote/speaker-diarization-3.1
Access to model is restricted and you are not in the authorized list
```

**解决方案**:
1. **【必须】先在网页上接受使用条款**（最重要！）:
   - 访问 https://huggingface.co/pyannote/speaker-diarization-3.1
   - 点击 **"Agree and access repository"** 按钮
   - 访问 https://huggingface.co/pyannote/segmentation-3.0
   - 同样点击 **"Agree and access repository"** 按钮
   - 等待几秒钟让权限生效

2. 确认已设置正确的 Token:
   - `export HUGGINGFACE_TOKEN=your_token_here`
   - 或 `export HF_TOKEN=your_token_here`

3. 检查网络连接

### 问题：CUDA 内存不足

**解决方案**:
- 减小音频文件大小
- 使用 CPU 模式（虽然较慢）
- 增加 GPU 内存或使用更小的模型

### 问题：任务一直处于 processing 状态

**解决方案**:
- 查看服务器日志了解详细错误
- 检查任务的 `error_message` 字段
- 重启服务

## 扩展功能

可以基于此服务扩展以下功能：

1. **WebSocket 支持**: 实时推送任务进度
2. **音频预处理**: 降噪、音量归一化
3. **多语言支持**: 根据音频自动检测语言
4. **说话人识别**: 训练说话人模型识别特定人物
5. **导出功能**: 导出为 SRT 字幕、Word 文档等
6. **批量处理**: 支持上传多个文件
7. **用户认证**: 添加 JWT 认证
8. **云存储**: 集成 S3/OSS 等云存储

## 许可证

请遵循 GLM-ASR 和 pyannote-audio 的相关许可证。
