import os
import sys
import logging
from dotenv import load_dotenv

# 加载 .env 文件
load_dotenv()

from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
from app.crew import HeimdallrCrew
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
    description="一个通过 API 接收文本并异步返回分析报告的智能诊断系统。",
    version="1.0.0"
)

# 定义请求体模型
class AnalyzeRequest(BaseModel):
    text: str

def run_crew_analysis(request: AnalyzeRequest):
    """用于在后台运行的 Crew 分析任务"""
    try:
        logger.info(f"开始分析任务，输入文本: '{request.text[:50]}...'")
        heimdallr_crew = HeimdallrCrew(request.text)
        crew = heimdallr_crew.setup_crew()
        result = crew.kickoff()
        logger.info(f"任务完成，最终报告:\n{result}")
    except Exception as e:
        logger.error(f"分析任务执行失败: {e}", exc_info=True)

@app.post("/analyze")
async def analyze_text(request: AnalyzeRequest, background_tasks: BackgroundTasks):
    """
    接收文本分析请求，立即返回确认，并在后台启动分析任务。
    """
    background_tasks.add_task(run_crew_analysis, request)
    return {"message": "Request received. Heimdallr is analyzing the issue..."}

@app.get("/")
async def root():
    return {"message": "Heimdallr is running."}

@app.get("/health")
async def health_check():
    """健康检查接口"""
    return {
        "status": "healthy",
        "service": "Heimdallr AI Diagnosis Assistant",
        "version": "1.0.0"
    }

# 如果直接运行此文件，用于本地开发
if __name__ == "__main__":
    logger.info("启动 Heimdallr AI 诊断助手...")
    
    if not check_environment():
        sys.exit(1)
    
    import uvicorn
    logger.info("启动 FastAPI 服务器...")
    logger.info(f"API 文档: http://localhost:{os.getenv('PORT', '8000')}/docs")
    
    try:
        uvicorn.run(
            app, 
            host="0.0.0.0", 
            port=int(os.getenv("PORT", "8000")),
            reload=False,
            log_level=os.getenv("LOG_LEVEL", "info").lower()
        )
    except KeyboardInterrupt:
        logger.info("服务已停止")
    except Exception as e:
        logger.error(f"启动失败: {e}", exc_info=True)
        sys.exit(1)