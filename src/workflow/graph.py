"""
轻量版工作流 — 不依赖 LangGraph，纯 Python 实现
大幅降低内存占用，适配 Streamlit Cloud 免费层（1GB RAM）
流程：搜索 → 分析 → 核查 → [条件分支] → 写作
"""
import asyncio
import logging
from src.agents.search_agent import search_agent
from src.agents.analysis_agent import analysis_agent
from src.agents.fact_check_agent import fact_check_agent
from src.agents.writing_agent import writing_agent
from src.config import settings

logger = logging.getLogger(__name__)

RESEARCH_TIMEOUT = 180


def _merge_state(state: dict, update: dict) -> dict:
    """合并状态更新，处理 messages 的追加语义"""
    for key, value in update.items():
        if key == "messages":
            state["messages"] = state.get("messages", []) + value
        else:
            state[key] = value
    return state


async def run_research(topic: str) -> dict:
    """执行完整研究流程（轻量版，无线程、无 LangGraph）"""
    state = {
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
        async def _run():
            max_rounds = settings.research.max_rounds
            threshold = settings.research.credibility_threshold

            for round_idx in range(max_rounds):
                # 1. 搜索
                search_result = await search_agent(state)
                _merge_state(state, search_result)

                # 2. 分析
                analysis_result = analysis_agent(state)
                _merge_state(state, analysis_result)

                # 3. 核查
                check_result = fact_check_agent(state)
                _merge_state(state, check_result)

                # 判断是否需要补充检索
                cred = state.get("credibility_score", 0)
                has_low = any(
                    f.get("credibility") == "low"
                    for f in state.get("verified_findings", [])
                )

                if cred < threshold and has_low and round_idx < max_rounds - 1:
                    state["needs_more_research"] = True
                    state["messages"].append(
                        f"[系统] 可信度 {cred:.2f} < 阈值 {threshold}，触发第 {round_idx + 2} 轮补充检索"
                    )
                    continue
                else:
                    state["needs_more_research"] = False
                    break

            # 4. 写作
            write_result = writing_agent(state)
            _merge_state(state, write_result)

        await asyncio.wait_for(_run(), timeout=RESEARCH_TIMEOUT)

    except asyncio.TimeoutError:
        logger.error(f"研究超时 ({RESEARCH_TIMEOUT}s)")
        state["report"] = f"# 研究报告：{topic}\n\n## 一、摘要\n\n研究过程超时，未能完成完整分析。请重试。"
        state["credibility_score"] = 0.0
        state["messages"] = [f"[系统] 研究超时 ({RESEARCH_TIMEOUT}秒)"]
    except Exception as e:
        logger.error(f"研究流程异常: {e}", exc_info=True)
        state["report"] = f"# 研究报告：{topic}\n\n## 一、摘要\n\n研究过程出现异常: {e}"
        state["credibility_score"] = 0.0
        state["messages"] = [f"[系统] 研究异常: {e}"]

    return {
        "topic": topic,
        "report": state.get("report", ""),
        "credibility_score": state.get("credibility_score", 0.0),
        "sub_questions": state.get("sub_questions", []),
        "verified_findings": state.get("verified_findings", []),
        "research_rounds": state.get("research_round", 1),
        "process_log": state.get("messages", []),
    }
