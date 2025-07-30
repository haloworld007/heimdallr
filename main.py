import os
import sys
import logging
from dotenv import load_dotenv

# 加载 .env 文件
load_dotenv()

from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
from app.heimdallr_flow import HeimdallrFlow
from app.logging_config import setup_logging

# 在应用启动时配置日志
setup_logging()

# 获取一个日志记录器实例
logger = logging.getLogger(__name__)


def check_environment():
    """检查环境变量配置"""
    openai_key = os.getenv("OPENAI_API_KEY")
    if not openai_key:
        logger.error("未找到API密钥配置: OPENAI_API_KEY")
        return False
    logger.info("✅ 检测到 OpenAI API 密钥")
    return True


# 初始化 FastAPI 应用
app = FastAPI(
    title="Heimdallr: AI 诊断助手",
    description="一个通过 Flow 架构进行智能诊断的 AI 系统，支持告警、Jira 工单、日志查询等多种输入类型。",
    version="2.0.0",
)


# 定义请求体模型
class AnalyzeRequest(BaseModel):
    text: str


# 定义响应模型
class AnalyzeResponse(BaseModel):
    success: bool
    message: str
    analysis_result: str = None
    metadata: dict = None


def run_flow_analysis(request: AnalyzeRequest):
    """用于在后台运行的 Flow 分析任务"""
    try:
        logger.info(f"开始 Flow 分析任务，输入文本: '{request.text[:50]}...'")
        
        # 创建 Heimdallr Flow 实例并执行分析
        flow = HeimdallrFlow(input_text=request.text)
        result = flow.kickoff()
        
        # 提取分析结果
        final_report = flow.state.final_report if flow.state.final_report else "分析完成，但未生成报告"
        
        # 构建分析摘要
        analysis_summary = {
            "flow_id": flow.state.flow_id,
            "input_classification": {
                "type": flow.state.classification.input_type.value if flow.state.classification else "unknown",
                "confidence": flow.state.classification.confidence if flow.state.classification else 0.0,
                "reasoning": flow.state.classification.reasoning if flow.state.classification else ""
            },
            "workflow_executed": flow.state.current_workflow,
            "tasks_completed": len(flow.state.completed_tasks),
            "tasks_failed": len(flow.state.failed_tasks),
            "execution_time": flow.state.total_execution_time,
            "progress": flow.state.get_workflow_progress()
        }
        
        logger.info(f"Flow 分析任务完成，工作流: {flow.state.current_workflow}, "
                   f"完成任务: {len(flow.state.completed_tasks)}, "
                   f"耗时: {flow.state.total_execution_time:.2f}s")
        logger.debug(f"最终报告:\n{final_report}")
        
        # 这里可以将结果存储到数据库或缓存中，供后续查询
        # 暂时只记录到日志
        
    except Exception as e:
        logger.error(f"Flow 分析任务执行失败: {e}", exc_info=True)


@app.post("/analyze", response_model=dict)
async def analyze_text(request: AnalyzeRequest, background_tasks: BackgroundTasks):
    """
    接收文本分析请求，立即返回确认，并在后台启动分析任务。
    支持多种输入类型：告警信息、Jira 工单、日志查询等。
    """
    try:
        # 验证输入
        if not request.text or len(request.text.strip()) < 3:
            return {
                "success": False,
                "message": "输入文本太短，至少需要3个字符",
                "request_id": None
            }
        
        # 生成请求ID
        import uuid
        request_id = str(uuid.uuid4())
        
        # 在后台启动分析任务
        background_tasks.add_task(run_flow_analysis, request)
        
        logger.info(f"接收到分析请求 {request_id}，文本长度: {len(request.text)}")
        
        return {
            "success": True,
            "message": "分析请求已接收，Heimdallr 正在后台进行智能诊断...",
            "request_id": request_id,
            "estimated_time": "预计30-60秒完成"
        }
        
    except Exception as e:
        logger.error(f"处理分析请求失败: {e}", exc_info=True)
        return {
            "success": False,
            "message": f"请求处理失败: {str(e)}",
            "request_id": None
        }


@app.post("/analyze-sync", response_model=AnalyzeResponse)
def analyze_text_sync(request: AnalyzeRequest):
    """
    同步分析接口 - 直接返回分析结果（用于测试或小规模使用）
    """
    try:
        logger.info(f"收到同步分析请求，文本长度: {len(request.text)}")
        
        # 验证输入
        if not request.text or len(request.text.strip()) < 3:
            return AnalyzeResponse(
                success=False,
                message="输入文本太短，至少需要3个字符"
            )
        
        # 创建 Heimdallr Flow 实例并执行分析
        flow = HeimdallrFlow(input_text=request.text)
        result = flow.kickoff()
        
        # 提取最终报告
        final_report = flow.state.final_report if flow.state.final_report else "分析完成，但未生成报告"
        
        # 构建详细的分析结果
        analysis_summary = {
            "flow_id": flow.state.flow_id,
            "input_classification": {
                "type": flow.state.classification.input_type.value if flow.state.classification else "unknown",
                "confidence": flow.state.classification.confidence if flow.state.classification else 0.0,
                "reasoning": flow.state.classification.reasoning if flow.state.classification else ""
            },
            "workflow_executed": flow.state.current_workflow,
            "tasks_completed": len(flow.state.completed_tasks),
            "tasks_failed": len(flow.state.failed_tasks),
            "execution_time": flow.state.total_execution_time,
            "progress": flow.state.get_workflow_progress()
        }
        
        # 返回结果
        return AnalyzeResponse(
            success=True,
            message="分析完成",
            analysis_result=final_report,
            metadata=analysis_summary
        )
        
    except Exception as e:
        logger.error(f"同步分析过程中发生错误: {e}", exc_info=True)
        return AnalyzeResponse(
            success=False,
            message=f"分析失败: {str(e)}"
        )


@app.get("/")
async def root():
    return {
        "message": "Heimdallr AI 诊断助手正在运行",
        "version": "2.0.0",
        "features": [
            "多类型输入智能识别",
            "动态工作流路由",
            "并行任务执行",
            "专业化 AI 智能体",
            "综合诊断报告"
        ]
    }


@app.get("/health")
async def health_check():
    """健康检查接口"""
    try:
        # 简单检查环境是否正确配置
        api_key_configured = bool(os.getenv("OPENAI_API_KEY"))
        
        return {
            "status": "healthy" if api_key_configured else "degraded",
            "service": "Heimdallr AI Diagnosis Assistant",
            "version": "2.0.0",
            "architecture": "CrewAI Flow + Dynamic Workflow Router",
            "api_key_configured": api_key_configured,
            "supported_input_types": ["alert", "jira_issue", "log_query", "hybrid", "unknown"]
        }
    except Exception as e:
        logger.error(f"健康检查失败: {e}")
        return {
            "status": "unhealthy",
            "error": str(e)
        }


@app.get("/capabilities")
async def get_capabilities():
    """获取系统能力描述"""
    return {
        "input_types": {
            "alert": "告警信息分析 - 支持系统告警、错误信息、性能问题等",
            "jira_issue": "Jira 工单分析 - 支持工单信息提取、分类、技术组件识别等",
            "log_query": "日志查询分析 - 支持日志搜索、模式识别、异常检测等",
            "hybrid": "混合类型 - 包含多种信息类型的复合分析",
            "unknown": "未知类型 - 尝试通用分析"
        },
        "workflow_features": {
            "intelligent_classification": "智能输入分类",
            "dynamic_routing": "动态工作流路由",
            "parallel_execution": "并行任务执行",
            "specialized_agents": "专业化 AI 智能体",
            "comprehensive_reporting": "综合诊断报告"
        },
        "analysis_stages": [
            "输入分类和模式提取",
            "动态工作流选择",
            "专业化分析执行",
            "时间线重建",
            "根因假设生成",
            "假设验证",
            "解决方案设计",
            "综合报告生成"
        ]
    }


# 如果直接运行此文件，用于本地开发
if __name__ == "__main__":
    logger.info("启动 Heimdallr AI 诊断助手 v2.0...")

    if not check_environment():
        sys.exit(1)

    import uvicorn

    logger.info("启动 FastAPI 服务器...")
    logger.info(f"API 文档: http://localhost:{os.getenv('PORT', '8000')}/docs")
    logger.info(f"同步分析接口: POST /analyze-sync")
    logger.info(f"异步分析接口: POST /analyze")
    logger.info(f"系统能力: GET /capabilities")

    try:
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=int(os.getenv("PORT", "8000")),
            reload=False,
            log_level=os.getenv("LOG_LEVEL", "info").lower(),
        )
    except KeyboardInterrupt:
        logger.info("服务已停止")
    except Exception as e:
        logger.error(f"启动失败: {e}", exc_info=True)
        sys.exit(1)
