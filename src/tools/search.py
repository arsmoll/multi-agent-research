"""
Tavily 搜索工具封装 — 多智能体协作研究系统
提供 Web 搜索能力，支持并行多查询检索
包含超时处理和错误降级
"""
import asyncio
import logging
from tavily import AsyncTavilyClient
from src.config import settings

logger = logging.getLogger(__name__)

SEARCH_TIMEOUT = 30  # 单次搜索超时秒数


class SearchTool:
    """Tavily 搜索工具，支持并行检索（懒加载）"""

    def __init__(self):
        self._client = None
        self.max_results = settings.tavily.max_results

    @property
    def client(self):
        if self._client is None:
            self._client = AsyncTavilyClient(api_key=settings.tavily.api_key)
        return self._client

    async def search(self, query: str) -> list[dict]:
        """单个查询搜索（带超时）"""
        try:
            result = await asyncio.wait_for(
                self.client.search(
                    query=query,
                    max_results=self.max_results,
                    search_depth="advanced",
                    include_answer=True,
                ),
                timeout=SEARCH_TIMEOUT,
            )
            return result.get("results", [])
        except asyncio.TimeoutError:
            logger.warning(f"搜索超时: {query[:50]}")
            return []
        except Exception as e:
            logger.warning(f"搜索失败: {query[:50]} — {e}")
            return []

    async def search_batch(self, queries: list[str]) -> dict[str, list[dict]]:
        """并行多查询搜索（带超时 + 错误降级）"""
        tasks = [self.search(q) for q in queries]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        return {
            query: (result if not isinstance(result, Exception) else [])
            for query, result in zip(queries, results)
        }


search_tool = SearchTool()
