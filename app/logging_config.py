import logging
import os
import sys
from dotenv import load_dotenv

# 加载环境变量，以便可以从 .env 文件中读取 LOG_LEVEL
load_dotenv()

def setup_logging():
    """配置全局日志记录器。"""
    # 从环境变量获取日志级别，默认为 INFO
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    
    # 定义日志格式
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # 配置基础日志
    logging.basicConfig(
        level=log_level,
        format=log_format,
        stream=sys.stdout,  # 将日志输出到标准输出
        force=True # 强制重新配置，在某些环境中需要
    )

    # 可以降低一些过于冗长的库的日志级别
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)

    print(f"✅ 日志功能已启动，级别: {log_level}")

