"""
分析 Agent — 多智能体协作研究系统
职责：从搜索结果中提取关键论断、数据和结构化信息
"""
import json
from src.llm.client import llm_client
from src.workflow.state import ResearchState

# 信息提取 Prompt
EXTRACTION_PROMPT = """你是一个信息分析专家。请从以下搜索结果中提取关键信息，结构化为研究发现。

搜索结果：
{search_results}

要求：
1. 提取关键论断（claim）、支撑数据（data）、来源（source_url）
2. 合并重复信息，保留不同来源的交叉引用
3. 每条发现应包含：claim（论断）、data（具体数据或证据）、source（来源URL列表）
4. 去除无关或低质量信息

请以 JSON 格式返回：
{{"findings": [
    {{"claim": "论断内容", "data": "数据/证据", "sources": ["url1", "url2"]}}
]}}"""


def analysis_agent(state: ResearchState) -> dict:
    """分析 Agent 节点

    1. 接收搜索 Agent 的原始结果
    2. LLM 提取关键论断和数据
    3. 结构化输出研究发现
    """
    search_results = state.get("search_results", [])
    if not search_results:
        return {
            "findings": [],
            "messages": ["[分析Agent] 无搜索结果可分析"],
        }

    # 截断过长的搜索结果以适应 token 限制
    truncated = []
    for r in search_results:
        content = r.get("content", "")[:800]
        truncated.append({
            "title": r.get("title", ""),
            "url": r.get("url", ""),
            "content": content,
        })

    results_text = json.dumps(truncated, ensure_ascii=False, indent=2)

    messages = [
        {"role": "system", "content": "你是一个信息分析专家，擅长从非结构化文本中提取关键信息和数据。"},
        {"role": "user", "content": EXTRACTION_PROMPT.format(search_results=results_text)},
    ]
    raw = llm_client.chat_json(messages, temperature=0.1)
    parsed = json.loads(raw)
    findings = parsed.get("findings", [])

    return {
        "findings": findings,
        "messages": [f"[分析Agent] 提取 {len(findings)} 条研究发现"],
    }
