# Heimdallr: AI 告警与 Issue 分析助手

## 开发入门

本项目基于 FastAPI 和 CrewAI 构建。以下是本地开发环境的启动和调试指南。

### 1. 环境设置

**创建虚拟环境**

```bash
python3 -m venv venv
```

**激活虚拟环境**

```bash
source venv/bin/activate
```

**安装依赖**

```bash
pip install -r requirements.txt
```

**配置环境变量**

复制 `env.example` 文件为 `.env`，并填入必要的 API 密钥。

```bash
cp env.example .env
```

### 2. 启动 Web 服务

执行以下命令以热重载模式启动 FastAPI 应用：

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

服务启动后，你可以通过两种方式进行测试：

**A) 使用自动生成的 API 文档 (推荐)**

FastAPI 会自动生成交互式的 API 文档。启动服务后，在浏览器中打开：

- **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)

你可以在这个页面上直接测试 `/analyze` 端点。

**B) 使用 cURL**

如果你偏好使用命令行，可以用 `curl` 发送请求：

```bash
curl -X POST http://localhost:8000/analyze \
-H "Content-Type: application/json" \
-d '{
    "text": "生产环境数据库主节点 CPU 使用率超过 90%，持续 5 分钟。"
}'
```