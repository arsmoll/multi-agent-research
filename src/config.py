"""
全局配置模块 — 极简版（无 pydantic 依赖）
从环境变量加载配置
"""
import os
from dotenv import load_dotenv

# 加载 .env 文件
load_dotenv()


class LLMConfig:
    """大模型配置"""
    def __init__(self):
        self.provider = os.getenv("LLM_PROVIDER", "deepseek")
        self.api_key = os.getenv(f"{self.provider.upper()}_API_KEY", "")
        self.base_url = os.getenv(f"{self.provider.upper()}_BASE_URL", "")
        self.model = os.getenv(f"{self.provider.upper()}_MODEL", "")
        self.temperature = float(os.getenv("LLM_TEMPERATURE", "0.3"))
        self.max_tokens = int(os.getenv("LLM_MAX_TOKENS", "4096"))


class TavilyConfig:
    """Tavily 搜索 API 配置"""
    def __init__(self):
        self.api_key = os.getenv("TAVILY_API_KEY", "")
        self.max_results = int(os.getenv("SEARCH_MAX_RESULTS", "5"))


class ResearchConfig:
    """研究流程参数"""
    def __init__(self):
        self.max_rounds = int(os.getenv("MAX_RESEARCH_ROUNDS", "2"))
        self.credibility_threshold = float(os.getenv("CREDIBILITY_THRESHOLD", "0.6"))


class ServiceConfig:
    """服务部署配置"""
    def __init__(self):
        self.host = os.getenv("API_HOST", "0.0.0.0")
        self.port = int(os.getenv("API_PORT", "8001"))


class Settings:
    """全局配置聚合"""
    def __init__(self):
        self.llm = LLMConfig()
        self.tavily = TavilyConfig()
        self.research = ResearchConfig()
        self.service = ServiceConfig()


# 全局配置单例
settings = Settings()
