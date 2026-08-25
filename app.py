"""
最小化测试 - 验证 Streamlit Cloud 基本部署
如果这个都不能运行，说明是环境/依赖问题，不是代码问题
"""
import streamlit as st

st.set_page_config(page_title="部署测试")
st.title("部署测试")
st.write("如果你看到这条消息，说明 Streamlit Cloud 基础部署正常！")
st.write("正在逐步恢复完整功能...")
