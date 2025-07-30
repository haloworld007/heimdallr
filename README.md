# Heimdallr

## 开发入门

本项目基于 FastAPI 和 CrewAI 构建，使用 `uv` 作为现代化的 Python 包管理器。以下是本地开发环境的启动和调试指南。

### 1. 前置要求

**安装 uv**

如果你还没有安装 uv，请先安装：

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# 或使用 pip
pip install uv
```

### 2. 环境设置

**一键设置开发环境**

uv 会自动管理 Python 版本和虚拟环境：

```bash
# 自动创建虚拟环境并安装所有依赖
uv sync
```

**配置环境变量**

复制 `env.example` 文件为 `.env`，并填入必要的 API 密钥：

```bash
cp env.example .env
```

**安装开发依赖（可选）**

如果需要开发工具（测试、代码格式化等）：

```bash
uv sync --extra dev
```

### 3. 启动 Web 服务

**开发模式（推荐）**

使用 uv 运行，自动激活虚拟环境：

```bash
# 开发模式，支持热重载
uv run uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

**生产模式**

```bash
# 生产模式
uv run python main.py
```

### 4. 测试服务

服务启动后，你可以通过以下方式进行测试：

**A) 使用自动生成的 API 文档（推荐）**

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

### 5. 开发工具

**添加新依赖**

```bash
# 添加生产依赖
uv add package-name

# 添加开发依赖
uv add --dev package-name
```

**代码格式化**

```bash
# 格式化代码
uv run black .
uv run isort .

# 类型检查
uv run mypy .
```

**运行测试**

```bash
uv run pytest
```

### 6. 项目结构

```
heimdallr/
├── pyproject.toml          # 项目配置和依赖管理
├── .python-version         # Python 版本锁定
├── uv.lock                # 精确依赖锁定文件（自动生成）
├── .env                   # 环境变量配置
├── main.py                # FastAPI 应用入口
├── app/                   # 应用核心代码
│   ├── crew.py           # CrewAI 编排
│   ├── agents/           # AI 智能体
│   ├── tasks/            # 任务定义
│   └── tools/            # 工具集
└── docs/                  # 文档
```
