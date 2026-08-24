"""
LangGraph 状态定义 — 多智能体协作研究系统
定义工作流中各节点共享的状态结构
"""
from typing import TypedDict, Annotated
from operator import add


class ResearchState(TypedDict):
    """多智能体研究工作流状态"""
    # 输入
    research_topic: str

    # 搜索 Agent 产出
    sub_questions: list[str]
    search_results: list[dict]

    # 分析 Agent 产出
    findings: list[dict]

    # 核查 Agent 产出
    verified_findings: list[dict]
    credibility_score: float
    needs_more_research: bool

    # 写作 Agent 产出
    report: str

    # 流程控制
    research_round: int
    messages: Annotated[list[str], add]
