"""
核查 Agent — 多智能体协作研究系统
职责：交叉验证研究发现，标注可信度（高/中/低）
"""
import json
import logging
from src.llm.client import llm_client
from src.config import settings
from src.workflow.state import ResearchState

logger = logging.getLogger(__name__)

FACT_CHECK_PROMPT = """你是一个事实核查专家。请对以下研究发现进行交叉验证，标注每条发现的可信度。

研究发现：
{findings}

核查标准：
- high（高可信度）：有 2 个以上独立来源支撑，数据一致
- medium（中可信度）：有 1-2 个来源支撑，但数据略有差异
- low（低可信度）：仅有 1 个来源，或来源不可靠，或数据矛盾

请以 JSON 格式返回：
{{"verified_findings": [
    {{
        "claim": "论断内容",
        "data": "数据/证据",
        "sources": ["url1", "url2"],
        "credibility": "high/medium/low",
        "verification_note": "核查说明"
    }}
]}}

同时返回整体可信度分数（0-1）：
{{"overall_score": 0.75}}"""


def fact_check_agent(state: ResearchState) -> dict:
    """核查 Agent 节点"""
    findings = state.get("findings", [])
    if not findings:
        return {
            "verified_findings": [],
            "credibility_score": 0.0,
            "needs_more_research": False,
            "messages": ["[核查Agent] 无发现需要核查"],
        }

    findings_text = json.dumps(findings, ensure_ascii=False, indent=2)

    try:
        messages = [
            {"role": "system", "content": "你是一个严谨的事实核查专家，擅长交叉验证信息的准确性和可靠性。"},
            {"role": "user", "content": FACT_CHECK_PROMPT.format(findings=findings_text)},
        ]
        raw = llm_client.chat_json(messages, temperature=0.1)
        parsed = json.loads(raw)
        verified = parsed.get("verified_findings", findings)
        overall_score = parsed.get("overall_score", 0.5)
    except Exception as e:
        logger.error(f"核查 Agent LLM 调用失败: {e}")
        # 降级：根据来源数量自动标注
        verified = []
        for f in findings:
            src_count = len(f.get("sources", []))
            cred = "high" if src_count >= 2 else "medium" if src_count == 1 else "low"
            f["credibility"] = cred
            f["verification_note"] = "自动标注（LLM 核查不可用）"
            verified.append(f)
        overall_score = 0.5

    threshold = settings.research.credibility_threshold
    max_rounds = settings.research.max_rounds
    current_round = state.get("research_round", 1)

    needs_more = (
        overall_score < threshold
        and current_round < max_rounds
        and any(f.get("credibility") == "low" for f in verified)
    )

    return {
        "verified_findings": verified,
        "credibility_score": overall_score,
        "needs_more_research": needs_more,
        "messages": [
            f"[核查Agent] 整体可信度 {overall_score:.2f}，"
            f"{'需要补充检索' if needs_more else '核查通过'}"
        ],
    }
