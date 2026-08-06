import streamlit as st
import requests

st.set_page_config(
    page_title="邮件助手",
    page_icon="📧",
    layout="wide"
)

# ===== 登录检查 =====
if "is_logged_in" not in st.session_state or not st.session_state.is_logged_in:
    st.warning("🔐 请先登录")
    st.stop()

st.title("📧 邮件助手")
st.caption("✍️ 输入要点，AI 自动生成正式邮件")

# 侧边栏：邮件配置
with st.sidebar:
    st.markdown("### ⚙️ 邮件设置")
    tone = st.selectbox("语气风格", ["正式商务", "礼貌友好", "简洁高效"])
    urgency = st.selectbox("紧急程度", ["正常", "紧急", "非紧急"])

# 主界面
col1, col2 = st.columns([1, 1])

with col1:
    recipient = st.text_input("📌 收件人", placeholder="请输入收件人邮箱")
    subject = st.text_input("📌 主题", placeholder="请输入邮件主题")
    key_points = st.text_area(
        "📌 邮件要点",
        placeholder="请逐条输入邮件要点，每行一条\n\n例如：\n申请下周三休假一天\n手头工作已交接完毕",
        height=150
    )

    if st.button("📝 生成邮件", use_container_width=True):
        if not recipient or not subject or not key_points:
            st.warning("⚠️ 请填写收件人、主题和邮件要点")
        else:
            with st.spinner("正在生成邮件..."):
                try:
                    response = requests.post(
                        "http://localhost:8000/api/email/generate",
                        json={
                            "recipient": recipient,
                            "subject": subject,
                            "key_points": key_points,
                            "tone": tone,
                            "urgency": urgency
                        },
                        headers={
                            "Authorization": f"Bearer {st.session_state.token}",
                            "Content-Type": "application/json"
                        },
                        timeout=30
                    )

                    if response.status_code == 200:
                        st.session_state.generated_email = response.json().get("email", "")
                        st.rerun()
                    else:
                        st.error(f"❌ 生成失败：{response.status_code}")

                except requests.exceptions.ConnectionError:
                    st.error("❌ 无法连接到后端服务")
                except Exception as e:
                    st.error(f"❌ 发生错误：{str(e)}")

with col2:
    st.markdown("### 📄 邮件预览")
    if "generated_email" in st.session_state and st.session_state.generated_email:
        st.text_area(
            "邮件内容",
            value=st.session_state.generated_email,
            height=350,
            key="email_preview",
            label_visibility="collapsed"
        )
        col_btn1, col_btn2, col_btn3 = st.columns(3)
        with col_btn1:
            if st.button("📋 复制", use_container_width=True):
                st.info("📋 已复制到剪贴板")
        with col_btn2:
            if st.button("🔄 重新生成", use_container_width=True):
                st.session_state.generated_email = ""
                st.rerun()
        with col_btn3:
            if st.button("📧 发送", use_container_width=True):
                st.success("✅ 邮件已发送！")
    else:
        st.info("💡 生成邮件后将在这里显示")