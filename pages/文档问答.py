import streamlit as st
import requests

st.set_page_config(
    page_title="文档问答",
    page_icon="📄",
    layout="wide"
)

# ===== 登录检查 =====
if "is_logged_in" not in st.session_state or not st.session_state.is_logged_in:
    st.warning("🔐 请先登录")
    st.stop()

st.title("📄 文档问答")
st.caption("📚 上传文档，AI 基于文档内容回答你的问题")

# ===== 初始化 =====
if "rag_messages" not in st.session_state:
    st.session_state.rag_messages = []

if "doc_loaded" not in st.session_state:
    st.session_state.doc_loaded = False

if "doc_name" not in st.session_state:
    st.session_state.doc_name = ""

# ===== 侧边栏：文档上传 =====
with st.sidebar:
    st.markdown("### 📤 上传文档")

    # 检查当前文档状态
    try:
        status_resp = requests.get(
            "http://localhost:8000/api/rag/status",
            headers={"Authorization": f"Bearer {st.session_state.token}"}
        )
        if status_resp.status_code == 200:
            data = status_resp.json()
            if data.get("loaded"):
                st.session_state.doc_loaded = True
                st.session_state.doc_name = data.get("doc_name", "")
    except:
        pass

    uploaded_file = st.file_uploader(
        "选择文档",
        type=["pdf", "txt", "md"],
        help="支持 PDF、TXT、Markdown 格式"
    )

    if uploaded_file is not None:
        if st.button("📚 加载文档", use_container_width=True):
            with st.spinner("正在加载文档..."):
                try:
                    files = {"file": (uploaded_file.name, uploaded_file.getvalue())}
                    response = requests.post(
                        "http://localhost:8000/api/rag/load",
                        files=files,
                        headers={"Authorization": f"Bearer {st.session_state.token}"},
                        timeout=60
                    )

                    if response.status_code == 200:
                        data = response.json()
                        if data.get("status") == "success":
                            st.session_state.doc_loaded = True
                            st.session_state.doc_name = uploaded_file.name
                            st.session_state.rag_messages = []
                            st.success(f"✅ 文档加载成功！共 {data.get('chunks', 0)} 个片段")
                            st.rerun()
                        else:
                            st.error(f"❌ {data.get('message', '加载失败')}")
                    else:
                        st.error(f"❌ 加载失败：{response.status_code}")

                except requests.exceptions.ConnectionError:
                    st.error("❌ 无法连接到后端服务")
                except Exception as e:
                    st.error(f"❌ 发生错误：{str(e)}")

    if st.session_state.doc_loaded:
        st.markdown("---")
        st.success(f"📄 {st.session_state.doc_name}")
        if st.button("🗑️ 卸载文档", use_container_width=True):
            try:
                requests.post(
                    "http://localhost:8000/api/rag/unload",
                    headers={"Authorization": f"Bearer {st.session_state.token}"}
                )
            except:
                pass
            st.session_state.doc_loaded = False
            st.session_state.doc_name = ""
            st.session_state.rag_messages = []
            st.rerun()

# ===== 主界面 =====
if not st.session_state.doc_loaded:
    st.info("👈 请先在左侧上传文档")
else:
    st.success(f"📄 当前文档：{st.session_state.doc_name}")

st.markdown("---")

# ===== 显示历史消息 =====
for msg in st.session_state.rag_messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])
        if msg["role"] == "assistant" and msg.get("sources"):
            with st.expander("📚 查看引用来源"):
                for i, source in enumerate(msg["sources"], 1):
                    st.markdown(f"**来源 {i}**")
                    st.code(source[:500], language="text")

# ===== 用户输入 =====
if prompt := st.chat_input("请输入你的问题..."):
    if not st.session_state.doc_loaded:
        st.warning("⚠️ 请先在左侧上传文档")
    else:
        st.session_state.rag_messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)

        with st.chat_message("assistant"):
            with st.spinner("🤔 检索中..."):
                try:
                    response = requests.post(
                        "http://localhost:8000/api/rag/query",
                        json={"question": prompt},
                        headers={
                            "Authorization": f"Bearer {st.session_state.token}",
                            "Content-Type": "application/json"
                        },
                        timeout=60
                    )

                    if response.status_code == 200:
                        data = response.json()
                        answer = data.get("answer", "没有收到回答")
                        sources = data.get("sources", [])

                        st.write(answer)

                        st.session_state.rag_messages.append({
                            "role": "assistant",
                            "content": answer,
                            "sources": sources
                        })

                        if sources:
                            with st.expander("📚 查看引用来源"):
                                for i, source in enumerate(sources, 1):
                                    st.markdown(f"**来源 {i}**")
                                    st.code(source[:500], language="text")
                    else:
                        st.error(f"❌ 查询失败：{response.status_code}")

                except requests.exceptions.ConnectionError:
                    st.error("❌ 无法连接到后端服务")
                except Exception as e:
                    st.error(f"❌ 发生错误：{str(e)}")