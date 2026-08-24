"""
Tavily 搜索工具封装 — 多智能体协作研究系统
提供 Web 搜索能力，支持并行多查询检索
"""
import asyncio
from tavily import AsyncTavilyClient
from src.config import settings


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
        """单个查询搜索

        Args:
            query: 搜索查询字符串

        Returns:
            搜索结果列表，每项包含 title/url/content/score
        """
        result = await self.client.search(
            query=query,
            max_results=self.max_results,
            search_depth="advanced",
            include_answer=True,
        )
        return result.get("results", [])

    async def search_batch(self, queries: list[str]) -> dict[str, list[dict]]:
        """并行多查询搜索

        Args:
            queries: 查询字符串列表

        Returns:
            以查询为 key、结果列表为 value 的字典
        """
        tasks = [self.search(q) for q in queries]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        return {
            query: (result if not isinstance(result, Exception) else [])
            for query, result in zip(queries, results)
        }


# 全局单例
search_tool = SearchTool()
