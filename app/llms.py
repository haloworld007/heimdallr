
import os
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from typing import Optional

class LLMManager:
    def __init__(self):
        # OpenAI 配置
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.openai_base_url = os.getenv("OPENAI_BASE_URL")  # 自定义API地址，比如代理或私有部署
        self.openai_organization = os.getenv("OPENAI_ORGANIZATION")  # 组织ID
        self.openai_default_model = os.getenv("OPENAI_DEFAULT_MODEL", "gpt-4-turbo")
        
        # Gemini 配置
        self.gemini_api_key = os.getenv("GEMINI_API_KEY")
        self.gemini_default_model = os.getenv("GEMINI_DEFAULT_MODEL", "gemini-pro")
        
        # 全局配置
        self.default_temperature = float(os.getenv("LLM_TEMPERATURE", "0.7"))
        self.request_timeout = int(os.getenv("LLM_TIMEOUT", "60"))  # 请求超时时间
        self.max_retries = int(os.getenv("LLM_MAX_RETRIES", "3"))  # 最大重试次数

        if not self.openai_api_key and not self.gemini_api_key:
            raise ValueError("错误：必须在 .env 文件中设置 OPENAI_API_KEY 或 GEMINI_API_KEY 中的至少一个。")

    def get_openai_llm(self, 
                       model: Optional[str] = None, 
                       temperature: Optional[float] = None,
                       base_url: Optional[str] = None,
                       organization: Optional[str] = None,
                       **kwargs):
        """
        创建 OpenAI LLM 实例
        
        Args:
            model: 模型名称，默认使用环境变量配置
            temperature: 温度参数，默认使用环境变量配置
            base_url: API地址，用于代理或私有部署
            organization: 组织ID
            **kwargs: 其他 ChatOpenAI 参数
        """
        if not self.openai_api_key:
            print("警告：未找到 OPENAI_API_KEY，无法创建 OpenAI LLM。将尝试使用备用模型。")
            return self.get_gemini_llm()
        
        # 使用传入参数或环境变量配置
        config = {
            "api_key": self.openai_api_key,
            "model": model or self.openai_default_model,
            "temperature": temperature if temperature is not None else self.default_temperature,
            "request_timeout": self.request_timeout,
            "max_retries": self.max_retries,
        }
        
        # 可选参数
        if base_url or self.openai_base_url:
            config["base_url"] = base_url or self.openai_base_url
            
        if organization or self.openai_organization:
            config["organization"] = organization or self.openai_organization
        
        # 合并额外参数
        config.update(kwargs)
        
        return ChatOpenAI(**config)

    def get_gemini_llm(self, 
                       model: Optional[str] = None, 
                       temperature: Optional[float] = None,
                       **kwargs):
        """
        创建 Gemini LLM 实例
        
        Args:
            model: 模型名称，默认使用环境变量配置
            temperature: 温度参数，默认使用环境变量配置
            **kwargs: 其他 ChatGoogleGenerativeAI 参数
        """
        if not self.gemini_api_key:
            print("警告：未找到 GEMINI_API_KEY，无法创建 Gemini LLM。将尝试使用备用模型。")
            return self.get_openai_llm()
        
        config = {
            "google_api_key": self.gemini_api_key,
            "model": model or self.gemini_default_model,
            "temperature": temperature if temperature is not None else self.default_temperature,
        }
        
        # 合并额外参数
        config.update(kwargs)
        
        return ChatGoogleGenerativeAI(**config)

    def get_fast_llm(self):
        """获取一个用于执行简单、快速任务的LLM。"""
        # 优先使用更经济的OpenAI模型，如果不可用则使用Gemini
        if self.openai_api_key:
            return self.get_openai_llm(
                model=os.getenv("OPENAI_FAST_MODEL", "gpt-3.5-turbo"), 
                temperature=0.3
            )
        return self.get_gemini_llm(temperature=0.3)

    def get_smart_llm(self):
        """获取一个用于执行复杂、需要深度推理任务的LLM。"""
        # 优先使用能力更强的GPT-4模型，如果不可用则使用Gemini
        if self.openai_api_key:
            return self.get_openai_llm(
                model=os.getenv("OPENAI_SMART_MODEL", "gpt-4-turbo"), 
                temperature=0.5
            )
        return self.get_gemini_llm(
            model=os.getenv("GEMINI_SMART_MODEL", "gemini-pro"),
            temperature=0.5
        )

    def get_llm_config_info(self):
        """获取当前LLM配置信息，用于调试"""
        return {
            "openai": {
                "has_key": bool(self.openai_api_key),
                "base_url": self.openai_base_url,
                "organization": self.openai_organization,
                "default_model": self.openai_default_model,
            },
            "gemini": {
                "has_key": bool(self.gemini_api_key),
                "default_model": self.gemini_default_model,
            },
            "global": {
                "temperature": self.default_temperature,
                "timeout": self.request_timeout,
                "max_retries": self.max_retries,
            }
        }

# 创建一个全局实例，方便在项目中其他地方直接导入和使用
llm_manager = LLMManager()
