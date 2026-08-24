"""
Streamlit 交互界面 — 多智能体协作研究系统
设计参考：Vercel Geist / Apple HIG
部署模式：直接调用 LangGraph 工作流，无需独立后端
"""
import asyncio
import threading
import time
import uuid
import streamlit as st
from src.workflow.graph import run_research

st.set_page_config(
    page_title="多智能体研究系统",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ─────────────────────── 后台任务管理 ───────────────────────
_tasks = {}

def _run_research_task(task_id: str, topic: str):
    holder = _tasks[task_id]
    try:
        result = asyncio.run(run_research(topic))
        holder["status"] = "completed"
        holder["result"] = result
    except Exception as e:
        holder["status"] = "failed"
        holder["error"] = str(e)

def start_research(topic: str) -> str:
    task_id = str(uuid.uuid4())[:8]
    _tasks[task_id] = {
        "status": "running",
        "topic": topic,
        "result": None,
        "start_time": time.time(),
    }
    thread = threading.Thread(target=_run_research_task, args=(task_id, topic), daemon=True)
    thread.start()
    return task_id

def get_research_status(task_id: str) -> dict:
    return _tasks.get(task_id, {})

# ─────────────────────── 设计系统 ───────────────────────
st.markdown("""
<style>
:root {
    --bg: #fafafa;
    --bg-card: #ffffff;
    --bg-subtle: #f4f4f5;

    --ink-1: #171717;
    --ink-2: #4d4d4d;
    --ink-3: #71717a;
    --ink-4: #a1a1aa;

    --line: rgba(0, 0, 0, 0.08);
    --line-faint: rgba(0, 0, 0, 0.04);

    --accent: #171717;
    --accent-hover: #27272a;
    --green: #16a34a;
    --amber: #d97706;
    --red: #dc2626;

    --r-xs: 3px; --r-sm: 5px; --r-md: 8px; --r-lg: 12px;

    --font-sans: -apple-system, BlinkMacSystemFont, "Segoe UI",
        "PingFang SC", "Microsoft YaHei", sans-serif;
    --font-mono: "SF Mono", "JetBrains Mono", ui-monospace, "Consolas", monospace;
}

.stApp {
    background: var(--bg);
    font-family: var(--font-sans);
    color: var(--ink-1);
    -webkit-font-smoothing: antialiased;
}
.main .block-container {
    max-width: 800px;
    padding: 64px 32px 96px;
}

.stApp h1 {
    font-size: 26px; font-weight: 600; line-height: 1.15;
    letter-spacing: -0.02em; color: var(--ink-1);
    margin-bottom: 6px;
}
.stApp h2 {
    font-size: 17px; font-weight: 600; line-height: 1.3;
    color: var(--ink-1); margin-top: 28px; margin-bottom: 8px;
}
.stApp h3 {
    font-size: 15px; font-weight: 600; line-height: 1.3;
    color: var(--ink-1); margin-top: 20px; margin-bottom: 6px;
}
.stApp p {
    font-size: 14px; line-height: 1.65; font-weight: 400;
    color: var(--ink-2);
}
.stApp strong { font-weight: 500; color: var(--ink-1); }

.stApp hr {
    border: none;
    border-top: 1px solid var(--line);
    margin: 40px 0;
}

section[data-testid="stSidebar"] {
    background: var(--bg-card);
    border-right: 1px solid var(--line);
}
section[data-testid="stSidebar"] .block-container { padding: 24px 16px; }
section[data-testid="stSidebar"] h2 {
    font-size: 12px; font-weight: 500; color: var(--ink-4);
    text-transform: uppercase; letter-spacing: 0.04em;
}

.stTextArea textarea {
    border: 1px solid var(--line) !important;
    border-radius: var(--r-md) !important;
    background: var(--bg-card) !important;
    font-size: 14px !important;
    font-family: var(--font-sans) !important;
    padding: 12px 14px !important;
    transition: border-color 200ms ease !important;
}
.stTextArea textarea:focus {
    border-color: var(--ink-1) !important;
    box-shadow: none !important;
    outline: none !important;
}
.stTextArea textarea::placeholder { color: var(--ink-4); }

.stTextInput > label, .stTextArea > label {
    font-size: 13px !important;
    font-weight: 500 !important;
    color: var(--ink-3) !important;
    margin-bottom: 6px !important;
}

.stButton > button {
    background: var(--accent) !important;
    color: #fff !important;
    border: none !important;
    border-radius: var(--r-md) !important;
    padding: 8px 20px !important;
    font-size: 14px !important;
    font-weight: 500 !important;
    font-family: var(--font-sans) !important;
    letter-spacing: -0.01em !important;
    transition: background 200ms ease !important;
    box-shadow: none !important;
}
.stButton > button:hover {
    background: var(--accent-hover) !important;
    box-shadow: none !important;
    border-color: transparent !important;
}
.stButton > button:active { background: var(--accent-hover) !important; }
.stButton > button:disabled {
    background: var(--bg-subtle) !important;
    color: var(--ink-4) !important;
    cursor: not-allowed;
}

.stProgress > div > div {
    background: var(--ink-1) !important;
    border-radius: 9999px !important;
}
.stProgress > div {
    background: var(--line) !important;
    border-radius: 9999px !important;
    height: 3px !important;
}
.stProgress p, .stProgress span {
    font-size: 12px !important;
    color: var(--ink-3) !important;
}

details {
    border: 1px solid var(--line) !important;
    border-radius: var(--r-md) !important;
    background: transparent !important;
}
details summary {
    font-size: 13px !important;
    font-weight: 500 !important;
    color: var(--ink-3) !important;
    padding: 10px 14px !important;
}
details[open] summary { border-bottom: 1px solid var(--line-faint); }

.steps { margin: 12px 0 32px; }
.step {
    padding: 14px 0;
    border-bottom: 1px solid var(--line-faint);
}
.step:last-child { border-bottom: none; }
.step-row {
    display: flex;
    align-items: baseline;
    gap: 10px;
}
.step-num {
    font-family: var(--font-mono);
    font-size: 12px;
    font-weight: 500;
    color: var(--ink-4);
    min-width: 22px;
}
.step.active .step-num { color: var(--ink-1); }
.step.done .step-num { color: var(--green); }
.step-title {
    font-size: 14px;
    font-weight: 500;
    color: var(--ink-1);
    flex: 1;
}
.step:not(.active):not(.done) .step-title { color: var(--ink-4); }
.step-status {
    font-size: 12px;
    font-weight: 500;
    font-family: var(--font-mono);
    color: var(--ink-4);
}
.step-status.done { color: var(--green); }
.step-status.active { color: var(--ink-1); }
.step-detail {
    font-size: 13px;
    color: var(--ink-3);
    margin-top: 3px;
    padding-left: 32px;
}

.stats {
    display: flex;
    align-items: baseline;
    gap: 28px;
    padding: 20px 0;
    border-top: 1px solid var(--line);
    border-bottom: 1px solid var(--line);
    margin: 28px 0 36px;
}
.stat { display: flex; align-items: baseline; gap: 6px; }
.stat-value {
    font-family: var(--font-mono);
    font-size: 22px;
    font-weight: 600;
    color: var(--ink-1);
    line-height: 1;
    font-variant-numeric: tabular-nums;
}
.stat-label {
    font-size: 13px;
    color: var(--ink-3);
}
.stat-sep {
    width: 1px;
    height: 14px;
    background: var(--line);
}

.stMarkdown h1 { font-size: 20px; font-weight: 600; margin: 28px 0 10px; }
.stMarkdown h2 {
    font-size: 16px; font-weight: 600;
    margin: 24px 0 8px;
    padding-bottom: 6px;
    border-bottom: 1px solid var(--line-faint);
}
.stMarkdown h3 { font-size: 14px; font-weight: 600; margin: 18px 0 6px; }
.stMarkdown p { font-size: 14px; line-height: 1.7; color: var(--ink-2); margin-bottom: 10px; }
.stMarkdown ul, .stMarkdown ol { margin-left: 20px; margin-bottom: 10px; }
.stMarkdown li { font-size: 14px; line-height: 1.7; color: var(--ink-2); margin-bottom: 4px; }
.stMarkdown strong { font-weight: 500; color: var(--ink-1); }
.stMarkdown table {
    width: 100%; border-collapse: collapse; margin: 10px 0; font-size: 13px;
}
.stMarkdown th {
    text-align: left; padding: 6px 10px;
    border-bottom: 1px solid var(--line);
    font-weight: 500; color: var(--ink-1);
    background: var(--bg-subtle);
}
.stMarkdown td {
    padding: 6px 10px;
    border-bottom: 1px solid var(--line-faint);
    color: var(--ink-2);
}
.stMarkdown code {
    font-family: var(--font-mono);
    font-size: 13px;
    background: var(--bg-subtle);
    padding: 1px 5px;
    border-radius: var(--r-xs);
}

.hint {
    font-size: 13px;
    color: var(--ink-4);
    margin-top: 48px;
    line-height: 1.6;
}

.stAlert { border-radius: var(--r-md) !important; }

@media (prefers-reduced-motion: reduce) {
    * { transition: none !important; animation: none !important; }
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────── 侧边栏 ───────────────────────
with st.sidebar:
    st.markdown("## 架构")
    st.markdown("""
    <p style="font-size:13px;color:var(--ink-3);line-height:1.6;">
        基于 LangGraph Supervisor 模式编排四个专职 Agent，
        核查不通过时自动触发补充检索。
    </p>
    """, unsafe_allow_html=True)

# ─────────────────────── 主页面 ───────────────────────
st.markdown("# 多智能体协作研究系统")
st.markdown("输入研究主题，系统将自动完成搜索、分析、核查与报告生成。")

st.markdown('<p style="font-size:13px;font-weight:500;color:var(--ink-3);margin-top:28px;margin-bottom:6px;">研究主题</p>', unsafe_allow_html=True)
topic = st.text_area(
    "研究主题",
    placeholder="例如：2024年中国新能源汽车出口趋势与竞争格局分析",
    height=72,
    key="research_topic",
    label_visibility="collapsed",
)

col_spacer, col_btn = st.columns([5, 1])
with col_btn:
    start_btn = st.button("开始研究", type="primary", use_container_width=True)

# ── 空状态 ──
if not st.session_state.get("research_started") and not start_btn:
    st.markdown(
        '<p class="hint">输入研究主题后，系统将通过搜索、分析、核查、写作四个阶段协作完成端到端研究。'
        '核查阶段可信度不足时，将自动触发补充检索。</p>',
        unsafe_allow_html=True,
    )

# ─────────────────────── 研究流程 ───────────────────────
if start_btn and topic.strip():
    st.session_state["research_started"] = True
    st.session_state["research_topic_value"] = topic.strip()
    task_id = start_research(topic.strip())
    st.session_state["task_id"] = task_id

if st.session_state.get("research_started"):
    research_topic = st.session_state["research_topic_value"]
    task_id = st.session_state.get("task_id")

    if not task_id or task_id not in _tasks:
        st.error("任务不存在，请重新开始研究。")
        st.session_state["research_started"] = False
    else:
        task = get_research_status(task_id)

        st.markdown(
            f'<p style="font-size:15px;font-weight:500;color:var(--ink-1);margin-top:28px;margin-bottom:4px;">{research_topic}</p>',
            unsafe_allow_html=True,
        )

        agent_steps = [
            ("search", "01", "搜索", "子问题拆分 + Tavily 并行检索"),
            ("analyze", "02", "分析", "关键论断与数据提取"),
            ("fact_check", "03", "核查", "交叉验证 + 可信度标注"),
            ("write", "04", "写作", "四段式报告生成"),
        ]

        flow_placeholder = st.empty()

        if task["status"] == "completed":
            result = task["result"]
            credibility = result.get("credibility_score", 0)
            rounds = result.get("research_rounds", 1)
            sub_count = len(result.get("sub_questions", []))

            steps_html = '<div class="steps">'
            for sid, num, name, desc in agent_steps:
                steps_html += f"""
                <div class="step done">
                    <div class="step-row">
                        <span class="step-num">{num}</span>
                        <span class="step-title">{name}</span>
                        <span class="step-status done">done</span>
                    </div>
                    <div class="step-detail">{desc}</div>
                </div>"""
            steps_html += '</div>'
            flow_placeholder.markdown(steps_html, unsafe_allow_html=True)

            if credibility >= 0.7:
                cred_color = "var(--green)"
            elif credibility >= 0.5:
                cred_color = "var(--amber)"
            else:
                cred_color = "var(--red)"

            st.markdown(f"""
            <div class="stats">
                <div class="stat">
                    <span class="stat-value" style="color:{cred_color};">{credibility:.0%}</span>
                    <span class="stat-label">可信度</span>
                </div>
                <div class="stat-sep"></div>
                <div class="stat">
                    <span class="stat-value">{rounds}</span>
                    <span class="stat-label">检索轮次</span>
                </div>
                <div class="stat-sep"></div>
                <div class="stat">
                    <span class="stat-value">{sub_count}</span>
                    <span class="stat-label">子问题</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("---")
            report = result.get("report", "无报告内容")
            st.markdown(report)

            if result.get("sub_questions"):
                with st.expander("检索子问题"):
                    for i, q in enumerate(result["sub_questions"], 1):
                        st.markdown(f"{i}. {q}")

            if result.get("process_log"):
                with st.expander("协作日志"):
                    for log in result["process_log"]:
                        st.text(log)

        elif task["status"] == "failed":
            steps_html = '<div class="steps">'
            for i, (sid, num, name, desc) in enumerate(agent_steps):
                steps_html += f"""
                <div class="step">
                    <div class="step-row">
                        <span class="step-num">{num}</span>
                        <span class="step-title">{name}</span>
                        <span class="step-status" style="color:var(--red);">failed</span>
                    </div>
                    <div class="step-detail">{desc}</div>
                </div>"""
            steps_html += '</div>'
            flow_placeholder.markdown(steps_html, unsafe_allow_html=True)
            st.error(f"研究失败：{task.get('error', '未知错误')}")

        else:
            # 估算进度
            elapsed = time.time() - task["start_time"]
            if elapsed < 12:
                current_step = 0
            elif elapsed < 24:
                current_step = 1
            elif elapsed < 34:
                current_step = 2
            else:
                current_step = 3

            pct = min(int((current_step / len(agent_steps)) * 85) + 10, 90)

            steps_html = '<div class="steps">'
            for i, (sid, num, name, desc) in enumerate(agent_steps):
                if i < current_step:
                    steps_html += f"""
                    <div class="step done">
                        <div class="step-row">
                            <span class="step-num">{num}</span>
                            <span class="step-title">{name}</span>
                            <span class="step-status done">done</span>
                        </div>
                        <div class="step-detail">{desc}</div>
                    </div>"""
                elif i == current_step:
                    steps_html += f"""
                    <div class="step active">
                        <div class="step-row">
                            <span class="step-num">{num}</span>
                            <span class="step-title">{name}</span>
                            <span class="step-status active">running</span>
                        </div>
                        <div class="step-detail">{desc}</div>
                    </div>"""
                else:
                    steps_html += f"""
                    <div class="step">
                        <div class="step-row">
                            <span class="step-num">{num}</span>
                            <span class="step-title">{name}</span>
                        </div>
                        <div class="step-detail">{desc}</div>
                    </div>"""
            steps_html += '</div>'
            flow_placeholder.markdown(steps_html, unsafe_allow_html=True)

            st.progress(pct, text=f"{agent_steps[current_step][2]} Agent 执行中...")
            time.sleep(2)
            st.rerun()
