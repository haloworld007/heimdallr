import os
import sys
from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
from dotenv import load_dotenv
from app.crew import HeimdallrCrew
from app.llms import llm_manager

# 加载 .env 文件
load_dotenv()

def check_environment():
    """检查环境变量配置"""
    openai_key = os.getenv("OPENAI_API_KEY")
    gemini_key = os.getenv("GEMINI_API_KEY")
    
    if not openai_key and not gemini_key:
        print("❌ 错误: 未找到API密钥配置")
        print("请在项目根目录创建 .env 文件，并配置以下变量之一:")
        print("  OPENAI_API_KEY=your_openai_api_key")
        print("  GEMINI_API_KEY=your_gemini_api_key")
        print("\n参考 env.example 文件查看配置示例")
        return False
    
    if openai_key:
        print("✅ 检测到 OpenAI API 密钥")
    if gemini_key:
        print("✅ 检测到 Gemini API 密钥")
    
    return True

# 初始化 FastAPI 应用
app = FastAPI(
    title="Heimdallr: AI 告警与 Issue 分析助手",
    description="一个通过 API 接收告警并异步返回分析报告的智能系统。",
    version="1.0.0"
)

# 定义请求体模型
class AnalyzeRequest(BaseModel):
    alert_text: str
    response_url: str

def run_crew_analysis(request: AnalyzeRequest):
    """用于在后台运行的 Crew 分析任务"""
    try:
        print(f"开始分析任务，告警: {request.alert_text}")
        heimdallr_crew = HeimdallrCrew(request.alert_text, request.response_url)
        crew = heimdallr_crew.setup_crew()
        result = crew.kickoff()
        print(f"任务完成，最终报告: {result}")
    except Exception as e:
        # 在实际生产中，这里应该有更健壮的错误处理和日志记录
        print(f"分析任务失败: {e}")

@app.post("/analyze")
async def analyze_alert(request: AnalyzeRequest, background_tasks: BackgroundTasks):
    """
    接收告警分析请求，立即返回确认，并在后台启动分析任务。
    """
    # 将耗时的分析任务添加到后台执行
    background_tasks.add_task(run_crew_analysis, request)
    
    # 立即返回响应
    return {"message": "Request received. Heimdallr is analyzing the issue..."}

@app.get("/")
async def root():
    return {"message": "Heimdallr is running."}

@app.get("/health")
async def health_check():
    """健康检查接口"""
    return {
        "status": "healthy",
        "service": "Heimdallr AI Alert & Issue Analyzer",
        "version": "1.0.0"
    }

@app.get("/config")
async def config_info():
    """获取LLM配置信息，用于调试"""
    try:
        config = llm_manager.get_llm_config_info()
        return {
            "status": "success",
            "config": config
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }

# 如果直接运行此文件，用于本地开发
if __name__ == "__main__":
    print("🏗️  启动 Heimdallr AI 告警与 Issue 分析助手...")
    
    # 检查环境配置
    if not check_environment():
        sys.exit(1)
    
    # 启动服务器
    import uvicorn
    print("🚀 启动 FastAPI 服务器...")
    print("📖 API 文档: http://localhost:8000/docs")
    print("🔍 健康检查: http://localhost:8000/health")
    print("⚙️  配置信息: http://localhost:8000/config")
    print("\n按 Ctrl+C 停止服务")
    
    try:
        uvicorn.run(
            app, 
            host="0.0.0.0", 
            port=int(os.getenv("PORT", "8000")),
            reload=False,  # 生产环境建议设为 False
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n👋 服务已停止")
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        sys.exit(1)