"""
LLM 客户端封装 — 极简版（基于 httpx，无 openai SDK 依赖）
支持 OpenAI 兼容 API，包含超时和重试机制
"""
import time
import json
import logging
import httpx
from src.config import settings
from typing import Optional

logger = logging.getLogger(__name__)


class LLMClient:
    """LLM 客户端，基于 httpx 直连 OpenAI 兼容 API（懒加载）"""

    def __init__(self):
        config = settings.llm
        self._client = None
        self.model = config.model
        self.temperature = config.temperature
        self.max_tokens = config.max_tokens
        self._api_key = config.api_key
        self._base_url = config.base_url.rstrip("/") if config.base_url else ""

    @property
    def client(self):
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=60.0)
        return self._client

    async def _chat_completion(self, messages, temperature=None, response_format=None):
        """异步调用 Chat Completions API"""
        url = f"{self._base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }
        body = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature if temperature is not None else self.temperature,
            "max_tokens": self.max_tokens,
        }
        if response_format:
            body["response_format"] = response_format

        resp = await self.client.post(url, headers=headers, json=body)
        resp.raise_for_status()
        data = resp.json()
        return data["choices"][0]["message"]["content"]

    async def chat_async(self, messages, temperature=None):
        """异步对话接口（带重试）"""
        last_err = None
        for attempt in range(3):
            try:
                return await self._chat_completion(messages, temperature=temperature)
            except Exception as e:
                last_err = e
                logger.warning(f"LLM 调用失败 (attempt {attempt+1}/3): {e}")
                if attempt < 2:
                    await self._async_sleep(2 * (attempt + 1))
        raise last_err

    async def chat_json_async(self, messages, temperature=0.1):
        """异步 JSON 格式输出（带重试）"""
        last_err = None
        for attempt in range(3):
            try:
                content = await self._chat_completion(
                    messages,
                    temperature=temperature,
                    response_format={"type": "json_object"},
                )
                # 验证 JSON 有效性
                json.loads(content)
                return content
            except json.JSONDecodeError as e:
                last_err = e
                logger.warning(f"LLM JSON 解析失败 (attempt {attempt+1}/3): {e}")
                if attempt < 2:
                    await self._async_sleep(2 * (attempt + 1))
            except Exception as e:
                last_err = e
                logger.warning(f"LLM JSON 调用失败 (attempt {attempt+1}/3): {e}")
                if attempt < 2:
                    await self._async_sleep(2 * (attempt + 1))
        raise last_err

    def chat(self, messages, temperature=None):
        """同步对话接口（带重试）"""
        import asyncio
        return asyncio.run(self.chat_async(messages, temperature=temperature))

    def chat_json(self, messages, temperature=0.1):
        """同步 JSON 格式输出（带重试）"""
        import asyncio
        return asyncio.run(self.chat_json_async(messages, temperature=temperature))

    @staticmethod
    async def _async_sleep(seconds):
        import asyncio
        await asyncio.sleep(seconds)


llm_client = LLMClient()
