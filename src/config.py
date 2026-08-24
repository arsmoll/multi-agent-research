"""
全局配置模块 — 多智能体协作研究系统
从环境变量加载配置，提供类型安全的访问接口
"""
import os
from dotenv import load_dotenv
from pydantic import BaseModel, Field

# 加载 .env 文件
load_dotenv()


class LLMConfig(BaseModel):
    """大模型配置"""
    provider: str = Field(default_factory=lambda: os.getenv("LLM_PROVIDER", "deepseek"))
    api_key: str = Field(default="")
    base_url: str = Field(default="")
    model: str = Field(default="")
    temperature: float = Field(default_factory=lambda: float(os.getenv("LLM_TEMPERATURE", "0.3")))
    max_tokens: int = Field(default_factory=lambda: int(os.getenv("LLM_MAX_TOKENS", "4096")))

    def __init__(self, **data):
        super().__init__(**data)
        provider = self.provider
        self.api_key = os.getenv(f"{provider.upper()}_API_KEY", "")
        self.base_url = os.getenv(f"{provider.upper()}_BASE_URL", "")
        self.model = os.getenv(f"{provider.upper()}_MODEL", "")


class TavilyConfig(BaseModel):
    """Tavily 搜索 API 配置"""
    api_key: str = Field(default_factory=lambda: os.getenv("TAVILY_API_KEY", ""))
    max_results: int = Field(default_factory=lambda: int(os.getenv("SEARCH_MAX_RESULTS", "5")))


class ResearchConfig(BaseModel):
    """研究流程参数"""
    max_rounds: int = Field(default_factory=lambda: int(os.getenv("MAX_RESEARCH_ROUNDS", "2")))
    credibility_threshold: float = Field(
        default_factory=lambda: float(os.getenv("CREDIBILITY_THRESHOLD", "0.6"))
    )


class ServiceConfig(BaseModel):
    """服务部署配置"""
    host: str = Field(default_factory=lambda: os.getenv("API_HOST", "0.0.0.0"))
    port: int = Field(default_factory=lambda: int(os.getenv("API_PORT", "8001")))


class Settings(BaseModel):
    """全局配置聚合"""
    llm: LLMConfig = Field(default_factory=LLMConfig)
    tavily: TavilyConfig = Field(default_factory=TavilyConfig)
    research: ResearchConfig = Field(default_factory=ResearchConfig)
    service: ServiceConfig = Field(default_factory=ServiceConfig)


# 全局配置单例
settings = Settings()
