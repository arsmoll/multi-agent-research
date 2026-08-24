"""
LangGraph 多智能体工作流编排 — 多智能体协作研究系统
Supervisor 模式：搜索 → 分析 → 核查 → [条件分支] → 写作
"""
from langgraph.graph import StateGraph, END
from src.workflow.state import ResearchState
from src.agents.search_agent import search_agent
from src.agents.analysis_agent import analysis_agent
from src.agents.fact_check_agent import fact_check_agent
from src.agents.writing_agent import writing_agent
from src.config import settings


def should_continue_research(state: ResearchState) -> str:
    """条件分支：判断核查后是否需要补充检索"""
    if state.get("needs_more_research", False):
        return "search"
    return "write"


def build_research_graph():
    """构建多智能体研究工作流图

    流程：
    1. search_agent — 拆分子问题 + 并行检索
    2. analysis_agent — 提取关键信息
    3. fact_check_agent — 交叉验证 + 可信度标注
    4. 条件分支：可信度不足 → 回到 search_agent 补充检索
    5. writing_agent — 生成四段式报告
    """
    graph = StateGraph(ResearchState)

    # 注册节点
    graph.add_node("search", search_agent)
    graph.add_node("analyze", analysis_agent)
    graph.add_node("fact_check", fact_check_agent)
    graph.add_node("write", writing_agent)

    # 设置入口
    graph.set_entry_point("search")

    # 线性边
    graph.add_edge("search", "analyze")
    graph.add_edge("analyze", "fact_check")

    # 条件边：核查后决定补充检索或进入写作
    graph.add_conditional_edges(
        "fact_check",
        should_continue_research,
        {
            "search": "search",
            "write": "write",
        },
    )

    # 写作节点 → 结束
    graph.add_edge("write", END)

    return graph.compile()


# 全局编译图实例
research_graph = build_research_graph()


async def run_research(topic: str) -> dict:
    """执行完整研究流程

    Args:
        topic: 研究主题

    Returns:
        包含报告和元数据的完整结果
    """
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

    final_state = await research_graph.ainvoke(initial_state)

    return {
        "topic": topic,
        "report": final_state.get("report", ""),
        "credibility_score": final_state.get("credibility_score", 0.0),
        "sub_questions": final_state.get("sub_questions", []),
        "verified_findings": final_state.get("verified_findings", []),
        "research_rounds": final_state.get("research_round", 1),
        "process_log": final_state.get("messages", []),
    }
