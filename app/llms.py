import os
import logging
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.language_models.chat_models import BaseChatModel
from config.llm_config import LLM_CONFIG

# 获取日志记录器
logger = logging.getLogger(__name__)

class LLMRegistry:
    """一个基于配置的、可根据服务商选择不同实现的智能 LLM 工厂。"""
    def __init__(self):
        self._llms = {}
        self._register_all()

    def _register_all(self):
        """读取配置并注册所有定义的 LLM。"""
        logger.info("开始注册所有 LLM...")
        for name, config in LLM_CONFIG.items():
            try:
                self._register(name, config)
            except Exception as e:
                logger.error(f"注册 LLM '{name}' 失败: {e}", exc_info=True)

    def _register(self, name: str, config: dict):
        """
        根据单个配置，使用最合适的 LangChain 类来注册一个 LLM 实例。
        """
        provider = config.get("provider", "openai").lower()
        model_name = config.get("model_name")
        api_key_env = config.get("api_key_env")
        base_url_env = config.get("base_url_env")

        if not all([model_name, api_key_env]):
            logger.error(f"LLM '{name}' 的配置不完整 (缺少 model_name 或 api_key_env)，跳过注册。")
            return

        api_key = os.getenv(api_key_env)
        if not api_key:
            logger.warning(f"未找到环境变量 '{api_key_env}'，跳过注册 LLM '{name}'。")
            return

        llm_instance = None
        
        # 构造 LiteLLM 能直接理解的、无歧义的模型标识符
        # 这是解决所有问题的核心
        model_identifier = f"{provider}/{model_name}"

        base_params = {"model": model_identifier, "api_key": api_key, "temperature": 0.7}

        if provider == "openai":
            if base_url_env and (base_url := os.getenv(base_url_env)):
                base_params["base_url"] = base_url
            llm_instance = ChatOpenAI(**base_params)
        
        else:
            logger.warning(f"不支持的服务商: '{provider}'。跳过注册 '{name}'。")
            return

        self._llms[name] = llm_instance
        logger.info(f"✅ 成功注册 LLM: '{name}' (标识: {model_identifier})。")

    def get(self, name: str) -> BaseChatModel:
        """
        从注册表中获取一个已命名的 LLM 实例。
        """
        llm = self._llms.get(name)
        if not llm:
            logger.error(f"请求的 LLM '{name}' 未被注册或注册失败。")
            raise ValueError(f"LLM '{name}' not found.")
        return llm

# 创建一个全局实例
llm_registry = LLMRegistry()
