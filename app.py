import streamlit as st

st.set_page_config(
    page_title="办公助手",
    page_icon="🤖",
    layout="wide"
)

# ===== 检查登录状态 =====
if "is_logged_in" not in st.session_state:
    st.session_state.is_logged_in = False

if "username" not in st.session_state:
    st.session_state.username = ""

# ===== 如果已登录 → 显示主界面 =====
if st.session_state.is_logged_in:
    st.title(f"👋 欢迎回来，{st.session_state.username}！")
    st.caption("请从左侧选择功能开始使用")
    
    with st.sidebar:
        st.markdown(f"👤 {st.session_state.username}")
        if st.button("🚪 退出登录"):
            st.session_state.is_logged_in = False
            st.session_state.username = ""
            st.rerun()
        st.markdown("---")
        st.page_link("pages/智能对话.py", label="💬 智能对话")
        st.page_link("pages/邮件助手.py", label="📧 邮件助手")
        st.page_link("pages/文档问答.py", label="📄 文档问答")
        st.page_link("pages/会议纪要.py", label="📝 会议纪要")

# ===== 如果未登录 → 只显示登录/注册入口 =====
else:
    with st.sidebar:
        st.page_link("pages/登录.py", label="🔐 登录")
        st.page_link("pages/注册.py", label="📝 注册")

    st.title("🤖 智能办公助手")
    st.markdown("""
    ### 请先登录或注册
    
    登录后您可以使用：
    - 💬 智能对话
    - 📧 邮件助手
    - 📄 文档问答
    - 📝 会议纪要
    """)