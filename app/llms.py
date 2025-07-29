import os
import logging
import litellm
from langchain_openai import ChatOpenAI
from typing import Optional

# 获取日志记录器
logger = logging.getLogger(__name__)

class LLMManager:
    """一个极简的、只支持单个 OpenAI 模型配置的 LLM 管理器。"""
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.base_url = os.getenv("OPENAI_BASE_URL")
        self.model = os.getenv("OPENAI_MODEL", "gpt-4-turbo")
        
        if not self.api_key:
            logger.error("未在环境变量中找到 OPENAI_API_KEY。LLM 将无法工作。")
            raise ValueError("OPENAI_API_KEY is not set.")

        # 兼容性修复：如果模型不是官方的 gpt- 系列，则为 litellm 创建一个别名
        # 这会告诉 litellm 将自定义模型（如 qwen-plus-latest）作为 openai 兼容模型处理
        if not self.model.startswith("gpt-"):
            # The format is {alias: "openai/actual_model_name"}
            # This tells litellm: "When you see `alias`, treat it as an openai model called `actual_model_name`"
            litellm.model_alias_map[self.model] = f"openai/{self.model}"
            logger.info(f"检测到自定义模型 '{self.model}'，已为其自动创建 litellm 别名。")

    def get_llm(self, temperature: float = 0.7, **kwargs) -> ChatOpenAI:
        """
        创建并返回一个 ChatOpenAI 实例。

        Args:
            temperature: 模型温度。
            **kwargs: 其他传递给 ChatOpenAI 的参数。

        Returns:
            一个 ChatOpenAI 实例。
        """
        config = {
            "model": self.model,
            "api_key": self.api_key,
            "temperature": temperature,
            **kwargs
        }

        if self.base_url:
            config["base_url"] = self.base_url
        
        logger.info(f"Final ChatOpenAI config: {config}")
        logger.debug(f"创建 LLM 实例，模型: {self.model}, 温度: {temperature}")
        return ChatOpenAI(**config)

    def get_llm_config_info(self) -> dict:
        """获取当前LLM配置信息，用于调试。"""
        return {
            "provider": "OpenAI",
            "model": self.model,
            "base_url": self.base_url or "https://api.openai.com/v1",
            "api_key_set": bool(self.api_key)
        }

# 创建一个全局实例
llm_manager = LLMManager()