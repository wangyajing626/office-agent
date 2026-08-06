import streamlit as st
import requests

# 这个页面不显示侧边栏
st.set_page_config(
    page_title="登录",
    page_icon="🔐",
    layout="centered"
)

# ===== 如果已经登录，直接跳转主页 =====
if st.session_state.get("is_logged_in", False):
    st.switch_page("app.py")
    st.stop()

st.title("🔐 用户登录")

with st.form("login_form"):
    username = st.text_input("👤 用户名", placeholder="请输入用户名")
    password = st.text_input("🔒 密码", type="password", placeholder="请输入密码")
    submitted = st.form_submit_button("🚀 登录", use_container_width=True)

if submitted:
    if not username or not password:
        st.error("❌ 用户名和密码不能为空")
    else:
        try:
            response = requests.post(
                "http://localhost:8000/api/users/login",
                json={"username": username, "password": password},
                timeout=10
            )
            if response.status_code == 200:
                data = response.json()
                st.session_state.is_logged_in = True
                st.session_state.username = data["username"]
                st.session_state.token = data.get("token", "")
                st.success("✅ 登录成功！正在进入系统...")
                import time
                time.sleep(0.3)
                st.switch_page("app.py")
            else:
                st.error(f"❌ {response.json().get('detail', '登录失败')}")
        except requests.exceptions.ConnectionError:
            st.error("❌ 无法连接到后端服务，请确保后端已启动")

st.markdown("---")
st.caption("还没有账号？去注册")
if st.button("📝 去注册"):
    st.switch_page("pages/注册.py")