import streamlit as st
import requests

st.set_page_config(
    page_title="会议纪要",
    page_icon="📝",
    layout="wide"
)

# ===== 登录检查 =====
if "is_logged_in" not in st.session_state or not st.session_state.is_logged_in:
    st.warning("🔐 请先登录")
    st.stop()

st.title("📝 会议纪要")
st.caption("🎙️ 上传录音 → 转文字 → AI 整理成结构化会议纪要")

# ===== 初始化 =====
if "transcript_text" not in st.session_state:
    st.session_state.transcript_text = ""

if "meeting_summary" not in st.session_state:
    st.session_state.meeting_summary = ""

# ===== 侧边栏 =====
with st.sidebar:
    st.markdown("### ⚙️ 会议设置")
    meeting_type = st.selectbox(
        "会议类型",
        ["项目评审", "团队周会", "需求评审", "技术方案讨论", "客户会议", "其他"]
    )

# ===== Tab 切换 =====
tab1, tab2 = st.tabs(["🎙️ 上传录音", "📝 粘贴文本"])

# ===== Tab 1: 上传录音 =====
with tab1:
    st.subheader("🎙️ 上传录音文件")

    uploaded_file = st.file_uploader(
        "选择录音文件",
        type=["wav", "mp3"],
        help="支持 WAV、MP3 格式，文件大小 ≤ 25MB"
    )

    if uploaded_file is not None:
        if st.button("🎤 转写", use_container_width=True):
            with st.spinner("正在转写..."):
                try:
                    files = {"file": (uploaded_file.name, uploaded_file.getvalue())}
                    response = requests.post(
                        "http://localhost:8000/api/meeting/transcribe",
                        files=files,
                        headers={"Authorization": f"Bearer {st.session_state.token}"},
                        timeout=60
                    )

                    if response.status_code == 200:
                        data = response.json()
                        st.session_state.transcript_text = data.get("text", "")
                        if not st.session_state.transcript_text.startswith("❌"):
                            st.success("✅ 转写完成！")
                            st.rerun()
                        else:
                            st.error(st.session_state.transcript_text)
                    else:
                        st.error(f"❌ 转写失败：{response.status_code}")

                except requests.exceptions.ConnectionError:
                    st.error("❌ 无法连接到后端服务")
                except Exception as e:
                    st.error(f"❌ 发生错误：{str(e)}")

    if st.session_state.transcript_text and not st.session_state.transcript_text.startswith("❌"):
        st.markdown("---")
        st.text_area("📝 转写结果", st.session_state.transcript_text, height=150, key="transcript_display")


# ===== Tab 2: 粘贴文本 =====
with tab2:
    st.subheader("📝 粘贴会议转写文本")
    transcript = st.text_area(
        "会议内容",
        placeholder="请粘贴会议录音转写的文本内容...",
        height=200,
        key="transcript_paste"
    )
    if transcript:
        st.session_state.transcript_text = transcript


# ===== 生成会议纪要 =====
if st.session_state.transcript_text and not st.session_state.transcript_text.startswith("❌"):
    st.markdown("---")

    col1, col2 = st.columns([1, 5])
    with col1:
        if st.button("🚀 生成纪要", use_container_width=True):
            with st.spinner("📝 AI 正在整理..."):
                try:
                    response = requests.post(
                        "http://localhost:8000/api/meeting/summarize",
                        json={
                            "transcript": st.session_state.transcript_text,
                            "meeting_type": meeting_type
                        },
                        headers={
                            "Authorization": f"Bearer {st.session_state.token}",
                            "Content-Type": "application/json"
                        },
                        timeout=60
                    )

                    if response.status_code == 200:
                        data = response.json()
                        st.session_state.meeting_summary = data.get("summary", "")
                        st.rerun()
                    else:
                        st.error(f"❌ 生成失败：{response.status_code}")

                except requests.exceptions.ConnectionError:
                    st.error("❌ 无法连接到后端服务")
                except Exception as e:
                    st.error(f"❌ 发生错误：{str(e)}")


# ===== 显示结果 =====
if st.session_state.meeting_summary:
    st.markdown("---")
    st.subheader("📄 会议纪要")

    col1, col2, col3 = st.columns([1, 1, 3])
    with col1:
        if st.button("📋 复制", use_container_width=True):
            st.info("📋 已复制到剪贴板")
    with col2:
        if st.button("🔄 重新生成", use_container_width=True):
            st.session_state.meeting_summary = ""
            st.rerun()
    with col3:
        if st.button("🗑️ 清空", use_container_width=True):
            st.session_state.meeting_summary = ""
            st.session_state.transcript_text = ""
            st.rerun()

    st.markdown(f"""
    <div style="background-color:#f8f9fa;border-radius:12px;padding:1.5rem 2rem;border-left:4px solid #667eea;line-height:1.8;white-space:pre-wrap;">
        {st.session_state.meeting_summary}
    </div>
    """, unsafe_allow_html=True)

    # 下载按钮
    st.download_button(
        label="📥 下载 Markdown",
        data=st.session_state.meeting_summary,
        file_name="会议纪要.md",
        mime="text/markdown",
        use_container_width=True
    )


# ===== 如果转写失败，显示错误信息 =====
elif st.session_state.transcript_text and st.session_state.transcript_text.startswith("❌"):
    st.error(st.session_state.transcript_text)
    if st.button("🗑️ 清除错误"):
        st.session_state.transcript_text = ""
        st.rerun()