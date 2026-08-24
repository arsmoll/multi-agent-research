"""
LLM 客户端封装 — 多智能体协作研究系统
提供统一的 LLM 调用接口，支持 OpenAI 兼容 API
"""
from openai import OpenAI
from src.config import settings


class LLMClient:
    """LLM 客户端，封装 OpenAI 兼容接口（懒加载）"""

    def __init__(self):
        config = settings.llm
        self._client = None
        self.model = config.model
        self.temperature = config.temperature
        self.max_tokens = config.max_tokens
        self._api_key = config.api_key
        self._base_url = config.base_url

    @property
    def client(self):
        if self._client is None:
            self._client = OpenAI(api_key=self._api_key, base_url=self._base_url)
        return self._client

    def chat(self, messages: list[dict], temperature: float | None = None) -> str:
        """同步对话接口

        Args:
            messages: OpenAI 消息格式 [{"role": ..., "content": ...}]
            temperature: 可选温度覆盖，None 则使用默认值

        Returns:
            模型回复文本
        """
        resp = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature if temperature is not None else self.temperature,
            max_tokens=self.max_tokens,
        )
        return resp.choices[0].message.content

    def chat_json(self, messages: list[dict], temperature: float = 0.1) -> str:
        """要求 JSON 格式输出的对话接口"""
        resp = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
            max_tokens=self.max_tokens,
            response_format={"type": "json_object"},
        )
        return resp.choices[0].message.content


# 全局单例
llm_client = LLMClient()
