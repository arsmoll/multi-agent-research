"""
Streamlit 交互界面 — 多智能体协作研究系统
稳定版：先注入环境变量，再延迟导入业务模块
"""
import os
import sys
import streamlit as st

# ── 第一步：从 Streamlit Secrets 注入环境变量 ──
# Streamlit Cloud 的 Secrets 不自动成为环境变量，需要手动注入
def _inject_secrets_to_env():
    """将 st.secrets 中的配置注入 os.environ，供下层模块读取"""
    try:
        secrets = st.secrets
        for key in secrets.keys():
            val = secrets[key]
            if isinstance(val, (str, int, float)):
                os.environ[key] = str(val)
    except Exception:
        # 本地开发没有 st.secrets 时忽略
        pass

_inject_secrets_to_env()

# ── 第二步：延迟导入业务模块 ──
# 在环境变量注入完成后再导入，确保配置正确
def _get_run_research():
    """延迟导入 run_research，返回 (函数, 错误信息)"""
    try:
        import asyncio
        from src.workflow.graph import run_research
        return run_research, None
    except Exception as e:
        import traceback
        return None, f"{e}\n\n{traceback.format_exc()}"


# ── 页面配置 ──
st.set_page_config(
    page_title="多智能体研究系统",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ── 样式 ──
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
.stApp hr { border: none; border-top: 1px solid var(--line); margin: 40px 0; }

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
}
.stTextArea textarea::placeholder { color: var(--ink-4); }

.stButton > button {
    background: var(--accent) !important;
    color: #fff !important;
    border: none !important;
    border-radius: var(--r-md) !important;
    padding: 8px 20px !important;
    font-size: 14px !important;
    font-weight: 500 !important;
    font-family: var(--font-sans) !important;
    transition: background 200ms ease !important;
    box-shadow: none !important;
}
.stButton > button:hover {
    background: var(--accent-hover) !important;
    box-shadow: none !important;
}
.stButton > button:disabled {
    background: var(--bg-subtle) !important;
    color: var(--ink-4) !important;
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

.stMarkdown h1 { font-size: 20px; font-weight: 600; margin: 28px 0 10px; }
.stMarkdown h2 {
    font-size: 16px; font-weight: 600; margin: 24px 0 8px;
    padding-bottom: 6px; border-bottom: 1px solid var(--line-faint);
}
.stMarkdown h3 { font-size: 14px; font-weight: 600; margin: 18px 0 6px; }
.stMarkdown p { font-size: 14px; line-height: 1.7; color: var(--ink-2); margin-bottom: 10px; }
.stMarkdown ul, .stMarkdown ol { margin-left: 20px; margin-bottom: 10px; }
.stMarkdown li { font-size: 14px; line-height: 1.7; color: var(--ink-2); margin-bottom: 4px; }
.stMarkdown strong { font-weight: 500; color: var(--ink-1); }
.stMarkdown table { width: 100%; border-collapse: collapse; margin: 10px 0; font-size: 13px; }
.stMarkdown th {
    text-align: left; padding: 6px 10px;
    border-bottom: 1px solid var(--line);
    font-weight: 500; color: var(--ink-1); background: var(--bg-subtle);
}
.stMarkdown td {
    padding: 6px 10px; border-bottom: 1px solid var(--line-faint); color: var(--ink-2);
}
.stMarkdown code {
    font-family: var(--font-mono); font-size: 13px;
    background: var(--bg-subtle); padding: 1px 5px; border-radius: var(--r-xs);
}

.stSpinner > div {
    color: var(--ink-3) !important;
    font-size: 14px !important;
}

.hint {
    font-size: 13px; color: var(--ink-4); margin-top: 48px; line-height: 1.6;
}
.stAlert { border-radius: var(--r-md) !important; }

@media (prefers-reduced-motion: reduce) {
    * { transition: none !important; animation: none !important; }
}
</style>
""", unsafe_allow_html=True)

# ── 侧边栏 ──
with st.sidebar:
    st.markdown("## 架构")
    st.markdown("""
    <p style="font-size:13px;color:var(--ink-3);line-height:1.6;">
        基于 LangGraph Supervisor 模式编排四个专职 Agent，
        核查不通过时自动触发补充检索。
    </p>
    """, unsafe_allow_html=True)

# ── 主页面 ──
st.markdown("# 多智能体协作研究系统")
st.markdown("输入研究主题，系统将自动完成搜索、分析、核查与报告生成。")

# ── 检查模块加载 ──
run_research, import_error = _get_run_research()

if import_error:
    st.error("应用初始化失败，请检查配置。")
    with st.expander("查看错误详情"):
        st.code(import_error)
    st.stop()

# ── 输入区 ──
st.markdown(
    '<p style="font-size:13px;font-weight:500;color:var(--ink-3);margin-top:28px;margin-bottom:6px;">研究主题</p>',
    unsafe_allow_html=True,
)
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
if not st.session_state.get("research_done") and not start_btn:
    st.markdown(
        '<p class="hint">输入研究主题后，系统将通过搜索、分析、核查、写作四个阶段协作完成端到端研究。'
        '核查阶段可信度不足时，将自动触发补充检索。</p>',
        unsafe_allow_html=True,
    )

# ── 研究执行 ──
if start_btn and topic.strip():
    st.session_state["research_done"] = False
    st.session_state["research_topic_value"] = topic.strip()
    st.session_state["research_result"] = None
    st.session_state["research_error"] = None

    import asyncio
    with st.spinner("正在执行多智能体协作研究，预计需要 30-90 秒..."):
        try:
            result = asyncio.run(run_research(topic.strip()))
            st.session_state["research_result"] = result
            st.session_state["research_done"] = True
        except Exception as e:
            import traceback
            st.session_state["research_error"] = f"{e}\n\n{traceback.format_exc()}"

    st.rerun()

# ── 结果展示 ──
if st.session_state.get("research_error"):
    st.error("研究过程中出现错误")
    with st.expander("查看错误详情"):
        st.code(st.session_state["research_error"])
    if st.button("重试", key="retry_btn"):
        st.session_state["research_error"] = None
        st.rerun()

elif st.session_state.get("research_done") and st.session_state.get("research_result"):
    result = st.session_state["research_result"]
    research_topic = st.session_state.get("research_topic_value", "")

    st.markdown(
        f'<p style="font-size:15px;font-weight:500;color:var(--ink-1);margin-top:28px;margin-bottom:4px;">{research_topic}</p>',
        unsafe_allow_html=True,
    )

    # 步骤展示
    agent_steps = [
        ("01", "搜索", "子问题拆分 + Tavily 并行检索"),
        ("02", "分析", "关键论断与数据提取"),
        ("03", "核查", "交叉验证 + 可信度标注"),
        ("04", "写作", "四段式报告生成"),
    ]

    steps_html = '<div style="margin:12px 0 32px;">'
    for num, name, desc in agent_steps:
        steps_html += f"""
        <div style="padding:14px 0;border-bottom:1px solid rgba(0,0,0,0.04);">
            <div style="display:flex;align-items:baseline;gap:10px;">
                <span style="font-family:var(--font-mono);font-size:12px;font-weight:500;color:#16a34a;min-width:22px;">{num}</span>
                <span style="font-size:14px;font-weight:500;color:#171717;flex:1;">{name}</span>
                <span style="font-size:12px;font-weight:500;font-family:var(--font-mono);color:#16a34a;">done</span>
            </div>
            <div style="font-size:13px;color:#71717a;margin-top:3px;padding-left:32px;">{desc}</div>
        </div>"""
    steps_html += '</div>'
    st.markdown(steps_html, unsafe_allow_html=True)

    # 指标
    credibility = result.get("credibility_score", 0)
    rounds = result.get("research_rounds", 1)
    sub_count = len(result.get("sub_questions", []))

    if credibility >= 0.7:
        cred_color = "#16a34a"
    elif credibility >= 0.5:
        cred_color = "#d97706"
    else:
        cred_color = "#dc2626"

    st.markdown(f"""
    <div style="display:flex;align-items:baseline;gap:28px;padding:20px 0;
        border-top:1px solid rgba(0,0,0,0.08);border-bottom:1px solid rgba(0,0,0,0.08);margin:28px 0 36px;">
        <div style="display:flex;align-items:baseline;gap:6px;">
            <span style="font-family:var(--font-mono);font-size:22px;font-weight:600;color:{cred_color};line-height:1;">{credibility:.0%}</span>
            <span style="font-size:13px;color:#71717a;">可信度</span>
        </div>
        <div style="width:1px;height:14px;background:rgba(0,0,0,0.08);"></div>
        <div style="display:flex;align-items:baseline;gap:6px;">
            <span style="font-family:var(--font-mono);font-size:22px;font-weight:600;color:#171717;line-height:1;">{rounds}</span>
            <span style="font-size:13px;color:#71717a;">检索轮次</span>
        </div>
        <div style="width:1px;height:14px;background:rgba(0,0,0,0.08);"></div>
        <div style="display:flex;align-items:baseline;gap:6px;">
            <span style="font-family:var(--font-mono);font-size:22px;font-weight:600;color:#171717;line-height:1;">{sub_count}</span>
            <span style="font-size:13px;color:#71717a;">子问题</span>
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

    st.markdown("---")
    if st.button("开始新研究", key="new_research_btn"):
        st.session_state["research_done"] = False
        st.session_state["research_result"] = None
        st.rerun()
