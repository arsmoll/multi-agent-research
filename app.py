"""
测试页面 - 验证所有依赖和模块加载
"""
import streamlit as st

st.set_page_config(page_title="依赖测试")
st.title("依赖加载测试")

# 测试 1: 基础
st.success("1. Streamlit 正常")

# 测试 2: openai
try:
    import openai
    st.success(f"2. openai 正常 (版本: {openai.__version__})")
except Exception as e:
    st.error(f"2. openai 失败: {e}")

# 测试 3: dotenv
try:
    from dotenv import load_dotenv
    st.success("3. python-dotenv 正常")
except Exception as e:
    st.error(f"3. python-dotenv 失败: {e}")

# 测试 4: pydantic
try:
    from pydantic import BaseModel
    import pydantic
    st.success(f"4. pydantic 正常 (版本: {pydantic.__version__})")
except Exception as e:
    st.error(f"4. pydantic 失败: {e}")

# 测试 5: httpx
try:
    import httpx
    st.success(f"5. httpx 正常 (版本: {httpx.__version__})")
except Exception as e:
    st.error(f"5. httpx 失败: {e}")

st.write("---")
st.write("如果所有项都是绿色 ✓，说明基础依赖全部正常。")
