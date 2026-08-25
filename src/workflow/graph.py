"""
LangGraph 多智能体工作流编排 — 多智能体协作研究系统
Supervisor 模式：搜索 → 分析 → 核查 → [条件分支] → 写作
"""
import asyncio
import logging
from langgraph.graph import StateGraph, END
from src.workflow.state import ResearchState
from src.agents.search_agent import search_agent
from src.agents.analysis_agent import analysis_agent
from src.agents.fact_check_agent import fact_check_agent
from src.agents.writing_agent import writing_agent
from src.config import settings

logger = logging.getLogger(__name__)

RESEARCH_TIMEOUT = 180  # 整体研究超时秒数


def should_continue_research(state: ResearchState) -> str:
    """条件分支：判断核查后是否需要补充检索"""
    if state.get("needs_more_research", False):
        return "search"
    return "write"


def build_research_graph():
    """构建多智能体研究工作流图"""
    graph = StateGraph(ResearchState)

    graph.add_node("search", search_agent)
    graph.add_node("analyze", analysis_agent)
    graph.add_node("fact_check", fact_check_agent)
    graph.add_node("write", writing_agent)

    graph.set_entry_point("search")

    graph.add_edge("search", "analyze")
    graph.add_edge("analyze", "fact_check")

    graph.add_conditional_edges(
        "fact_check",
        should_continue_research,
        {
            "search": "search",
            "write": "write",
        },
    )

    graph.add_edge("write", END)

    return graph.compile()


research_graph = build_research_graph()


async def run_research(topic: str) -> dict:
    """执行完整研究流程（带超时保护）"""
    initial_state = {
        "research_topic": topic,
        "sub_questions": [],
        "search_results": [],
        "findings": [],
        "verified_findings": [],
        "credibility_score": 0.0,
        "needs_more_research": False,
        "report": "",
        "research_round": 0,
        "messages": [],
    }

    try:
        final_state = await asyncio.wait_for(
            research_graph.ainvoke(initial_state),
            timeout=RESEARCH_TIMEOUT,
        )
    except asyncio.TimeoutError:
        logger.error(f"研究超时 ({RESEARCH_TIMEOUT}s)")
        final_state = {
            "report": f"# 研究报告：{topic}\n\n## 一、摘要\n\n研究过程超时，未能完成完整分析。请重试。",
            "credibility_score": 0.0,
            "sub_questions": [],
            "verified_findings": [],
            "research_round": 0,
            "messages": [f"[系统] 研究超时 ({RESEARCH_TIMEOUT}秒)"],
        }
    except Exception as e:
        logger.error(f"研究流程异常: {e}", exc_info=True)
        final_state = {
            "report": f"# 研究报告：{topic}\n\n## 一、摘要\n\n研究过程出现异常: {e}",
            "credibility_score": 0.0,
            "sub_questions": [],
            "verified_findings": [],
            "research_round": 0,
            "messages": [f"[系统] 研究异常: {e}"],
        }

    return {
        "topic": topic,
        "report": final_state.get("report", ""),
        "credibility_score": final_state.get("credibility_score", 0.0),
        "sub_questions": final_state.get("sub_questions", []),
        "verified_findings": final_state.get("verified_findings", []),
        "research_rounds": final_state.get("research_round", 1),
        "process_log": final_state.get("messages", []),
    }
