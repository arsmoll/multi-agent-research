"""
分析 Agent — 多智能体协作研究系统
职责：从搜索结果中提取关键论断、数据和结构化信息
"""
import json
import logging
from src.llm.client import llm_client
from src.workflow.state import ResearchState

logger = logging.getLogger(__name__)

EXTRACTION_PROMPT = """你是一个信息分析专家。请从以下搜索结果中提取关键信息，结构化为研究发现。

搜索结果：
{search_results}

要求：
1. 提取关键论断（claim）、支撑数据（data）、来源（source_url）
2. 合并重复信息，保留不同来源的交叉引用
3. 每条发现应包含：claim（论断）、data（数据/证据）、source（来源URL列表）
4. 去除无关或低质量信息

请以 JSON 格式返回：
{{"findings": [
    {{"claim": "论断内容", "data": "数据/证据", "sources": ["url1", "url2"]}}
]}}"""


async def analysis_agent(state: ResearchState) -> dict:
    """分析 Agent 节点"""
    search_results = state.get("search_results", [])
    if not search_results:
        return {
            "findings": [],
            "messages": ["[分析Agent] 无搜索结果可分析"],
        }

    truncated = []
    for r in search_results:
        content = r.get("content", "")[:800]
        truncated.append({
            "title": r.get("title", ""),
            "url": r.get("url", ""),
            "content": content,
        })

    results_text = json.dumps(truncated, ensure_ascii=False, indent=2)

    try:
        messages = [
            {"role": "system", "content": "你是一个信息分析专家，擅长从非结构化文本中提取关键信息和数据。"},
            {"role": "user", "content": EXTRACTION_PROMPT.format(search_results=results_text)},
        ]
        raw = await llm_client.chat_json_async(messages, temperature=0.1)
        parsed = json.loads(raw)
        findings = parsed.get("findings", [])
    except Exception as e:
        logger.error(f"分析 Agent LLM 调用失败: {e}")
        # 降级：从搜索结果中直接提取基本信息
        findings = []
        for r in search_results[:5]:
            findings.append({
                "claim": r.get("title", ""),
                "data": r.get("content", "")[:200],
                "sources": [r.get("url", "")],
            })

    return {
        "findings": findings,
        "messages": [f"[分析Agent] 提取 {len(findings)} 条研究发现"],
    }
