"""
搜索 Agent — 多智能体协作研究系统
职责：将研究主题拆分为子问题，并行检索 Web 信息
"""
import json
import logging
from src.llm.client import llm_client
from src.tools.search import search_tool
from src.workflow.state import ResearchState

logger = logging.getLogger(__name__)

SUBQUERY_PROMPT = """你是一个研究分析师。请将以下研究主题拆分为 3-5 个具体的、可搜索的子问题。

研究主题：{topic}

要求：
1. 子问题应覆盖主题的不同维度（定义/现状/数据/趋势/挑战）
2. 每个子问题应可以直接用于搜索引擎查询
3. 用中文表述

请以 JSON 格式返回：{{"sub_questions": ["问题1", "问题2", ...]}}"""


async def search_agent(state: ResearchState) -> dict:
    """搜索 Agent 节点"""
    topic = state["research_topic"]
    round_num = state.get("research_round", 0)

    if round_num > 0 and state.get("verified_findings"):
        low_credibility_findings = [
            f for f in state["verified_findings"] if f.get("credibility") == "low"
        ]
        if low_credibility_findings:
            topic = f"补充研究：{topic}，重点关注以下未验证信息：" + ", ".join(
                f.get("claim", "") for f in low_credibility_findings[:3]
            )

    # LLM 拆分子问题
    sub_questions = []
    try:
        messages = [
            {"role": "system", "content": "你是一个专业的研究分析师，擅长将复杂主题拆解为可搜索的子问题。"},
            {"role": "user", "content": SUBQUERY_PROMPT.format(topic=topic)},
        ]
        raw = await llm_client.chat_json_async(messages, temperature=0.2)
        parsed = json.loads(raw)
        sub_questions = parsed.get("sub_questions", [])[:5]
    except Exception as e:
        logger.warning(f"子问题拆分失败，使用原始主题: {e}")
        sub_questions = [topic]

    if not sub_questions:
        sub_questions = [topic]

    # 并行搜索
    try:
        search_data = await search_tool.search_batch(sub_questions)
    except Exception as e:
        logger.error(f"搜索全部失败: {e}")
        search_data = {q: [] for q in sub_questions}

    # 汇总
    all_results = []
    for query, results in search_data.items():
        for r in results:
            all_results.append({
                "query": query,
                "title": r.get("title", ""),
                "url": r.get("url", ""),
                "content": r.get("content", ""),
                "score": r.get("score", 0),
            })

    return {
        "sub_questions": sub_questions,
        "search_results": all_results,
        "research_round": round_num + 1,
        "messages": [f"[搜索Agent] 拆分 {len(sub_questions)} 个子问题，检索到 {len(all_results)} 条结果"],
    }
