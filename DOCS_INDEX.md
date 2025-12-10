# 📚 文档导航

欢迎使用语音识别服务！以下是各个文档的说明，帮助你快速找到需要的信息。

## 🚀 新手入门

如果你是第一次使用，按以下顺序阅读：

1. **[QUICKSTART.md](QUICKSTART.md)** - 快速开始指南
   - ⏱️ 5分钟快速上手
   - 📦 安装步骤
   - ✅ 基本测试

2. **[SERVICE_README.md](SERVICE_README.md)** - 详细使用文档
   - 📖 完整功能说明
   - 🔧 配置选项
   - 🐛 故障排查

3. **[PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)** - 项目总结
   - 🎯 技术架构
   - 📊 性能分析
   - 🔮 未来规划

## 📋 文档分类

### 快速参考
- **README.md** - 项目主页（GLM-ASR 介绍）
- **QUICKSTART.md** - 10分钟快速入门
- **MODEL_SETUP.md** - 模型下载指南

### 开发文档
- **SERVICE_README.md** - 服务使用手册
- **PROJECT_SUMMARY.md** - 技术文档

### 配置文件
- **.env.example** - 环境变量示例
- **config.example.json** - 服务配置示例

### 工具脚本
- **test_service.py** - Python 测试客户端
- **download_models.py** - 模型下载工具
- **start_service.sh** - 快速启动脚本
- **web_ui.html** - Web 界面示例
- **verify_setup.py** - 环境验证脚本

## 🎯 按需查找

### 我想...

#### 快速开始使用
➡️ 阅读 [QUICKSTART.md](QUICKSTART.md)

#### 下载模型
➡️ 阅读 [MODEL_SETUP.md](MODEL_SETUP.md)
➡️ 运行 `python download_models.py`

#### 了解 API 接口
➡️ 阅读 [SERVICE_README.md](SERVICE_README.md) 的 API 部分
➡️ 或访问 http://localhost:6006/docs （服务运行后）

#### 了解技术实现
➡️ 阅读 [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)
➡️ 查看 `service.py` 源代码

#### 解决问题
➡️ 阅读 [SERVICE_README.md](SERVICE_README.md) 的故障排查部分
➡️ 查看服务日志

#### 配置环境
➡️ 复制 `.env.example` 为 `.env`
➡️ 阅读 [QUICKSTART.md](QUICKSTART.md) 的准备工作

#### 部署到生产
➡️ 阅读 [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) 的安全建议
➡️ 使用 systemd 或 supervisor 管理服务

#### 进行二次开发
➡️ 阅读 [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) 的技术栈部分
➡️ 参考 `service.py` 和 `test_service.py`

## 📞 获取帮助

### 问题排查流程

1. **查看文档**
   - 先查看 [SERVICE_README.md](SERVICE_README.md) 的常见问题
   - 检查配置是否正确

2. **查看日志**
   ```bash
   # 查看服务日志
   python service.py
   ```

3. **测试连接**
   ```bash
   # 检查服务是否运行
   curl http://localhost:6006
   ```

4. **提交 Issue**
   - 提供错误日志
   - 说明运行环境
   - 描述复现步骤

## 🔗 快速链接

| 内容       | 文件                                     |
| ---------- | ---------------------------------------- |
| 快速开始   | [QUICKSTART.md](QUICKSTART.md)           |
| 模型下载   | [MODEL_SETUP.md](MODEL_SETUP.md)         |
| 使用手册   | [SERVICE_README.md](SERVICE_README.md)   |
| 技术文档   | [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) |
| 主服务代码 | [service.py](service.py)                 |
| 测试客户端 | [test_service.py](test_service.py)       |
| 模型下载工具 | [download_models.py](download_models.py) |
| 环境验证脚本 | [verify_setup.py](verify_setup.py)       |
| Web 界面   | [web_ui.html](web_ui.html)               |
| 环境配置   | [.env.example](.env.example)             |

## 📝 更新日志

- **2025-12-10**: 初始版本发布
  - ✅ 说话人分离功能
  - ✅ 语音转文字功能
  - ✅ RESTful API
  - ✅ SQLite 任务管理
  - ✅ Web 界面

---

**提示**: 所有文档都使用 Markdown 格式，可以在 GitHub 或任何 Markdown 阅读器中查看。
