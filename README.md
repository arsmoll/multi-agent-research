---
title: Multi-Agent Research System
emoji: 🔬
colorFrom: gray
colorTo: indigo
sdk: streamlit
app_file: app.py
pinned: false
license: mit
---

# 多智能体协作研究系统

基于 LangGraph 编排的多智能体协作研究系统，四个专职 Agent 分工完成从研究主题输入到结构化报告生成的端到端自动化。

## 架构

```
搜索 Agent → 分析 Agent → 核查 Agent → [条件分支] → 写作 Agent
```

| Agent | 职责 |
|---|---|
| 搜索 | LLM 子问题拆分 + Tavily API 并行检索 |
| 分析 | 关键论断与支撑数据提取，结构化输出 |
| 核查 | 跨来源交叉验证，标注高/中/低可信度 |
| 写作 | 四段式报告生成（摘要/关键发现/数据支撑/信息来源） |

核查阶段可信度不足时，系统自动回到搜索 Agent 补充检索，最多 2 轮。

## 技术栈

- **工作流编排**: LangGraph (StateGraph + 条件边)
- **LLM**: DeepSeek Chat (OpenAI 兼容接口)
- **搜索**: Tavily Search API
- **前端**: Streamlit
- **语言**: Python 3.11

## 本地运行

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 配置密钥
cp .env.example .env
# 编辑 .env 填入 DEEPSEEK_API_KEY 和 TAVILY_API_KEY

# 3. 启动
streamlit run app.py --server.port=8501
```

## 环境变量

| 变量 | 说明 |
|---|---|
| `DEEPSEEK_API_KEY` | DeepSeek API 密钥 |
| `TAVILY_API_KEY` | Tavily Search API 密钥 |
| `LLM_PROVIDER` | LLM 提供商 (默认 deepseek) |
| `LLM_TEMPERATURE` | 生成温度 (默认 0.3) |
| `MAX_RESEARCH_ROUNDS` | 最大补充检索轮次 (默认 2) |
| `CREDIBILITY_THRESHOLD` | 可信度阈值 (默认 0.6) |
