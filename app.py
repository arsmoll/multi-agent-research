"""
测试 httpx
"""
import streamlit as st

st.set_page_config(page_title="httpx 测试")
st.title("httpx 测试")

try:
    import httpx
    st.success(f"httpx 正常 (版本: {httpx.__version__})")
except Exception as e:
    st.error(f"httpx 失败: {e}")
