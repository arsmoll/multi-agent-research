"""
LLM 客户端封装 — 多智能体协作研究系统
提供统一的 LLM 调用接口，支持 OpenAI 兼容 API
包含超时处理和重试机制
"""
import time
import logging
from typing import Optional
from openai import OpenAI
from src.config import settings

logger = logging.getLogger(__name__)


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
            self._client = OpenAI(
                api_key=self._api_key,
                base_url=self._base_url,
                timeout=60.0,
                max_retries=2,
            )
        return self._client

    def chat(self, messages: list, temperature: Optional[float] = None) -> str:
        """同步对话接口（带重试）"""
        last_err = None
        for attempt in range(3):
            try:
                resp = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=temperature if temperature is not None else self.temperature,
                    max_tokens=self.max_tokens,
                )
                return resp.choices[0].message.content
            except Exception as e:
                last_err = e
                logger.warning(f"LLM 调用失败 (attempt {attempt+1}/3): {e}")
                if attempt < 2:
                    time.sleep(2 * (attempt + 1))
        raise last_err

    def chat_json(self, messages: list, temperature: float = 0.1) -> str:
        """要求 JSON 格式输出的对话接口（带重试）"""
        last_err = None
        for attempt in range(3):
            try:
                resp = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=self.max_tokens,
                    response_format={"type": "json_object"},
                )
                return resp.choices[0].message.content
            except Exception as e:
                last_err = e
                logger.warning(f"LLM JSON 调用失败 (attempt {attempt+1}/3): {e}")
                if attempt < 2:
                    time.sleep(2 * (attempt + 1))
        raise last_err


llm_client = LLMClient()
