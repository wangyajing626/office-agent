import streamlit as st
import requests

st.set_page_config(
    page_title="智能对话",
    page_icon="💬",
    layout="wide"
)

# ===== 登录检查（防止直接访问 URL）=====
if "is_logged_in" not in st.session_state or not st.session_state.is_logged_in:
    st.warning("🔐 请先登录")
    st.stop()

st.title("💬 智能对话助手")

if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = []

for msg in st.session_state.chat_messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

if prompt := st.chat_input("请输入你的问题..."):
    st.session_state.chat_messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    with st.chat_message("assistant"):
        with st.spinner("思考中..."):
            try:
                response = requests.post(
                    "http://localhost:8000/api/chat/send",
                    json={"message": prompt},
                    headers={
                        "Authorization": f"Bearer {st.session_state.token}",
                        "Content-Type": "application/json"
                    },
                    timeout=30
                )

                if response.status_code == 200:
                    data = response.json()
                    reply = data.get("reply", "没有收到回复")
                else:
                    reply = f"❌ 错误：{response.status_code}"

            except requests.exceptions.ConnectionError:
                reply = "❌ 无法连接到后端服务，请确保后端已启动"
            except Exception as e:
                reply = f"❌ 发生错误：{str(e)}"

        st.write(reply)
        st.session_state.chat_messages.append({"role": "assistant", "content": reply})