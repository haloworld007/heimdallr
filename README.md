# Heimdallr: AI 告警与 Issue 分析助手

## 1. 项目愿景 (Vision)

Heimdallr 是一个基于多 Agent 协作的智能分析系统，旨在通过一个标准的 Web API 端点，自动化处理和分析来自企业 IM 工具（如 Slack, Teams, 钉钉, Seatalk）的告警和 Issue。它通过模拟一个高效的运维团队，实现从告警接收、信息富化、根因定位到解决方案建议的全流程自动化，最终将分析报告通过回调机制发回给调用方，从而缩短故障响应时间 (MTTR)，提升运维效率。

## 2. 核心架构 (Core Architecture)

本项目结合了 **FastAPI** Web 框架和 **CrewAI** Agent 框架，构建了一个健壮、可扩展的异步处理服务。

### 2.1. 设计哲学

- **API 驱动 (API-First)**: 所有功能通过一个定义良好的 RESTful API 端点暴露，易于集成。
- **异步处理 (Asynchronous)**: 采用"立即确认，后台处理，最终回调"的模式，完美适应耗时的 AI 分析任务，避免调用方超时。
- **角色分明 (Role-Based)**: 每个 Agent 都有一个清晰、单一的职责，模拟真实团队中的专家角色。
- **流程驱动 (Process-Driven)**: 整个分析过程被定义为一个由多个任务组成的、严格按顺序执行的"工作流"或"标准操作程序 (SOP)"。
- **工具赋能 (Tool-Empowered)**: Agent 的能力由其配备的工具决定。工具是与外部世界（如数据库、日志系统、API）交互的唯一途径。

### 2.2. 核心组件

- **`main.py`**: 项目主入口。基于 **FastAPI** 构建，负责暴露 `/analyze` API 端点，接收请求，并启动后台分析任务。
- **`app/crew.py`**: 工作流编排中心。负责定义和组建 `Crew`，将不同的 Agent 和 Task 按照预设的顺序串联起来，并在任务结束后执行回调。
- **`app/agents/`**: Agent 定义目录。每个 Agent 的定义都在一个独立的文件中，实现了高度模块化。
- **`app/tasks/`**: 任务定义目录。每个具体的分析步骤被封装成一个独立的 `Task` 文件。
- **`app/llms.py`**: LLM 管理中心。集中管理和初始化多种语言模型（如 OpenAI, Gemini），并为不同复杂度的 Agent 分配最合适的模型。
- **`app/tools/`**: 自定义工具库。存放所有与外部系统交互的工具。
- **`requirements.txt`**: 项目的 Python 依赖清单。
- **`.env`**: 环境变量文件，用于安全地存储 API 密钥等敏感信息。

## 3. 核心工作流 (Core Workflow)

一个典型的告警分析流程如下：

1.  **接收 (Ingestion)**: 外部系统（如 Seatalk Bot）向 `POST /analyze` 端点发送请求，包含 `alert_text` 和 `response_url`。
2.  **确认 (Acknowledge)**: FastAPI 服务立即返回 `HTTP 200 OK`，并告知"正在分析"。
3.  **后台执行 (Execute)**: FastAPI 将 `HeimdallrCrew` 的执行放入后台任务中。工作流开始：
    1.  **告警分类 (Triage Task)**: `TriageAgent` 对原始告警进行分类。
    2.  **信息富化 (Enrichment Task)**: `EnrichmentAgent` 根据分类结果，调用工具拉取上下文信息。
    3.  **根因分析 (RCA Task)**: `RootCauseAnalysisAgent` 分析并确定根本原因。
    4.  **方案生成 (Solution Task)**: `SolutionsArchitectAgent` 提供解决方案。
    5.  **报告汇总 (Reporting Task)**: `CommunicationsOfficerAgent` 将所有结论整理成一份清晰的报告。
4.  **回调 (Callback)**: `ReportingTask` 完成后，通过其 `callback` 函数，将最终的 Markdown 报告发送到 `response_url`。

## 4. API 端点定义

- **Endpoint**: `POST /analyze`
- **Request Body**:
  ```json
  {
    "alert_text": "生产环境数据库主节点 CPU 使用率超过 90%，持续 5 分钟。",
    "response_url": "https://hook.seatalk.io/callback/unique_id_xyz"
  }
  ```
- **Success Response (Immediate)**:
  - **Code**: `200 OK`
  - **Body**:
    ```json
    {
      "message": "Request received. Heimdallr is analyzing the issue..."
    }
    ```
- **Callback (Later)**:
  - **Method**: `POST`
  - **URL**: The `response_url` from the initial request.
  - **Body**:
    ```json
    {
      "report": "## Heimdallr 分析报告\n\n**告警分类**: ...\n\n**根本原因**: ...\n\n**建议方案**: ..."
    }
    ```

## 5. 如何运行

1.  在 `.env` 文件中配置 `OPENAI_API_KEY` 和/或 `GEMINI_API_KEY`。
2.  安装所有依赖：
    ```bash
    pip install -r requirements.txt
    ```
3.  在项目根目录 (`Heimdallr/`) 下启动 FastAPI 服务：
    ```bash
    python main.py
    ```
4.  服务启动后，您可以使用任何 HTTP 客户端向 `http://localhost:8000/analyze` 发送请求进行测试。

## 6. 项目优化记录

### 最近完成的优化
- ✅ **类型提示增强**: 为所有Agent添加了完整的类型提示，提升IDE开发体验
- ✅ **搜索工具实现**: 完成了SearchTools类的具体实现，支持日志、指标、配置搜索
- ✅ **任务参数修复**: 修复了所有Task类的参数传递问题，支持context和callback
- ✅ **启动流程优化**: 整合环境检查到main.py，移除冗余的启动脚本
- ✅ **错误处理改进**: 添加了完善的异常捕获和友好的错误提示

### 规划中的功能
- 🔄 **巡检功能**: 主动式系统健康检查和预警
- 🔄 **Issue 分析增强**: 扩展对各类IT问题的分析能力
- 🔄 **集成扩展**: 支持更多监控系统和工具的接入