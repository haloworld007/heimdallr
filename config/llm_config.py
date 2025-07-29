# config/llm_config.py

"""
LLM 配置的唯一来源。
"""

import os

LLM_CONFIG = {
    "default": {
        "provider": "openai",
        "model_name": os.getenv("OPENAI_MODEL", "gpt-4-turbo"),
        "api_key_env": "OPENAI_API_KEY",
        "base_url_env": "OPENAI_BASE_URL",
    },
}