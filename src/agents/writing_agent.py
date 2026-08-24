"""
写作 Agent — 多智能体协作研究系统
职责：基于核查后的发现，生成四段式结构化研究报告
"""
from src.llm.client import llm_client
from src.workflow.state import ResearchState

# 报告生成 Prompt
REPORT_PROMPT = """你是一个专业的研究报告撰写专家。请基于以下经过核查的研究发现，撰写一份结构化研究报告。

研究主题：{topic}
研究发现：
{findings}

报告格式要求（严格遵循四段式结构）：

## 一、摘要
用 2-3 段概括研究主题的核心结论，让读者快速了解全貌。

## 二、关键发现
列出 3-5 条最重要的研究发现，每条包含：
- 核心论断
- 支撑数据
- 可信度标注（[高可信]/[中可信]/[低可信]）

## 三、数据支撑
汇总报告中的关键数据点，以表格或列表形式呈现，标注来源。

## 四、信息来源
列出所有引用的信息来源（URL），按可信度排序。

注意：
- 语言简洁专业，避免冗余
- 数据要有来源支撑
- 对可信度低的发现需注明「待进一步验证」"""


def writing_agent(state: ResearchState) -> dict:
    """写作 Agent 节点

    1. 接收核查后的研究发现
    2. LLM 生成四段式结构化报告
    3. 输出最终研究报告
    """
    topic = state["research_topic"]
    verified = state.get("verified_findings", [])

    if not verified:
        report = f"# 研究报告：{topic}\n\n## 一、摘要\n\n未能获取足够的研究信息，建议调整研究方向后重试。"
        return {
            "report": report,
            "messages": ["[写作Agent] 无有效发现，生成空报告"],
        }

    # 格式化发现数据供 LLM 使用
    findings_text = ""
    for i, f in enumerate(verified, 1):
        credibility = f.get("credibility", "unknown")
        cred_label = {"high": "高可信", "medium": "中可信", "low": "低可信"}.get(credibility, "未知")
        findings_text += f"\n{i}. 论断：{f.get('claim', '')}\n"
        findings_text += f"   数据：{f.get('data', '')}\n"
        findings_text += f"   可信度：{cred_label}\n"
        findings_text += f"   来源：{', '.join(f.get('sources', []))}\n"
        if f.get("verification_note"):
            findings_text += f"   核查说明：{f['verification_note']}\n"

    messages = [
        {"role": "system", "content": "你是一个专业的研究报告撰写专家，擅长将研究发现整合为清晰、结构化的报告。"},
        {"role": "user", "content": REPORT_PROMPT.format(topic=topic, findings=findings_text)},
    ]
    report = llm_client.chat(messages, temperature=0.4)

    return {
        "report": report,
        "messages": ["[写作Agent] 研究报告生成完成"],
    }
