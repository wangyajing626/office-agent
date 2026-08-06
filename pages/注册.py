import streamlit as st
import requests

st.set_page_config(
    page_title="注册",
    page_icon="📝",
    layout="centered"
)

if st.session_state.get("is_logged_in", False):
    st.switch_page("app.py")
    st.stop()

st.title("📝 用户注册")

with st.form("register_form"):
    username = st.text_input("👤 用户名", placeholder="请输入用户名")
    password = st.text_input("🔒 密码", type="password", placeholder="请输入密码（至少6位）")
    confirm_password = st.text_input("✅ 确认密码", type="password", placeholder="请再次输入密码")
    submitted = st.form_submit_button("🚀 注册", use_container_width=True)

if submitted:
    if not username or not password:
        st.error("❌ 用户名和密码不能为空")
    elif password != confirm_password:
        st.error("❌ 两次输入的密码不一致")
    elif len(password) < 6:
        st.error("❌ 密码至少6位")
    else:
        try:
            response = requests.post(
                "http://localhost:8000/api/users/register",
                json={"username": username, "password": password},
                timeout=10
            )
            if response.status_code == 200:
                st.success(f"✅ 注册成功！")
                st.session_state.registered_username = username
                st.info("正在跳转到登录页面...")
                import time
                time.sleep(0.5)
                st.switch_page("pages/登录.py")
            else:
                st.error(f"❌ {response.json().get('detail', '注册失败')}")
        except requests.exceptions.ConnectionError:
            st.error("❌ 无法连接到后端服务")

st.markdown("---")
st.caption("已有账号？去登录")
if st.button("🔐 去登录"):
    st.switch_page("pages/登录.py")