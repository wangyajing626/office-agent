import streamlit as st
from openai import OpenAI
import os
from dotenv import load_dotenv
import tempfile
from pathlib import Path

# ========== 页面配置 ==========
load_dotenv("config/.env")

st.set_page_config(
    page_title="文档问答",
    page_icon="📄",
    layout="wide"
)

# ========== CSS样式 ==========
st.markdown("""
<style>
    .main-title {
        font-size: 2.2rem;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        padding: 0.5rem 0;
    }
    .doc-status {
        background-color: #f0f4ff;
        border-radius: 12px;
        padding: 1rem 1.5rem;
        border-left: 4px solid #667eea;
    }
    .source-box {
        background-color: #f8f9fa;
        border-radius: 8px;
        padding: 0.75rem 1rem;
        border-left: 3px solid #667eea;
        margin: 0.5rem 0;
        font-size: 0.9rem;
        color: #4a5568;
    }
    .stButton button {
        border-radius: 20px !important;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        border: none !important;
        padding: 0.5rem 1.5rem !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
    }
    .stButton button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4) !important;
    }
</style>
""", unsafe_allow_html=True)

# ========== 标题 ==========
st.markdown('<div class="main-title">📄 文档问答</div>', unsafe_allow_html=True)
st.caption("📚 上传文档，AI 基于文档内容智能回答你的问题")

st.markdown("---")

# ========== 初始化 ==========
if "rag_messages" not in st.session_state:
    st.session_state.rag_messages = []

if "vectorstore" not in st.session_state:
    st.session_state.vectorstore = None

if "doc_loaded" not in st.session_state:
    st.session_state.doc_loaded = False

if "doc_name" not in st.session_state:
    st.session_state.doc_name = ""

# ========== 侧边栏：文档上传 ==========
with st.sidebar:
    st.subheader("📤 上传文档")
    
    uploaded_file = st.file_uploader(
        "选择文档",
        type=["pdf", "txt", "md"],
        help="支持 PDF、TXT、Markdown 格式"
    )
    
    if uploaded_file is not None:
        if st.button("📚 加载文档", use_container_width=True):
            with st.spinner("正在加载文档..."):
                try:
                    # 保存临时文件
                    with tempfile.NamedTemporaryFile(delete=False, suffix=Path(uploaded_file.name).suffix) as tmp_file:
                        tmp_file.write(uploaded_file.getvalue())
                        tmp_path = tmp_file.name
                    
                    # ===== 导入 =====
                    from langchain_community.document_loaders import PyPDFLoader, TextLoader
                    from langchain_text_splitters import RecursiveCharacterTextSplitter
                    from langchain_openai import OpenAIEmbeddings
                    from langchain_community.vectorstores import Chroma
                    
                    # 根据文件类型选择加载器
                    file_ext = Path(uploaded_file.name).suffix.lower()
                    if file_ext == ".pdf":
                        loader = PyPDFLoader(tmp_path)
                    else:
                        loader = TextLoader(tmp_path, encoding="utf-8")
                    
                    documents = loader.load()
                    
                    # 切片
                    text_splitter = RecursiveCharacterTextSplitter(
                        chunk_size=300,
                        chunk_overlap=30
                    )
                    chunks = text_splitter.split_documents(documents)
                    
                    # ===== 向量化：硅基流动 API =====
                    # ⚠️ 把你的硅基流动 API Key 填到下面
                    embeddings = OpenAIEmbeddings(
                        api_key="sk-hplkllqfpfwgsabebuslzhwjlkvtxkurjbmzcrhgfgdooqer",  # ← 替换成你的真实密钥
                        base_url="https://api.siliconflow.cn/v1",
                        model="Pro/BAAI/bge-m3"
                    )
                    
                    # 存入向量数据库
                    persist_dir = f"./data/chroma_db/{uploaded_file.name}"
                    vectorstore = Chroma.from_documents(
                        documents=chunks,
                        embedding=embeddings,
                        persist_directory=persist_dir
                    )
                    vectorstore.persist()
                    
                    st.session_state.vectorstore = vectorstore
                    st.session_state.doc_loaded = True
                    st.session_state.doc_name = uploaded_file.name
                    st.session_state.rag_messages = []
                    
                    # 清理临时文件
                    os.unlink(tmp_path)
                    
                    st.success(f"✅ 文档加载成功！共 {len(chunks)} 个片段")
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"❌ 加载失败：{e}")
    
    # 显示已加载的文档
    if st.session_state.doc_loaded:
        st.markdown("---")
        st.markdown(f"""
        <div class="doc-status">
            📄 已加载：<strong>{st.session_state.doc_name}</strong>
            <br>✅ 可以开始提问
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🗑️ 卸载文档", use_container_width=True):
            st.session_state.vectorstore = None
            st.session_state.doc_loaded = False
            st.session_state.doc_name = ""
            st.session_state.rag_messages = []
            st.rerun()
    else:
        st.info("💡 请上传文档开始使用")

# ========== 主页面 ==========
if not st.session_state.doc_loaded:
    st.info("👈 请在左侧上传文档，然后开始提问")
else:
    st.success(f"📄 当前文档：{st.session_state.doc_name}")

st.markdown("---")

# ========== 显示历史消息 ==========
for msg in st.session_state.rag_messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])
        
        if msg["role"] == "assistant" and "sources" in msg:
            with st.expander("📚 查看引用来源"):
                for i, source in enumerate(msg["sources"], 1):
                    st.markdown(f"""
                    <div class="source-box">
                        <strong>来源 {i}</strong><br>
                        {source[:300]}...
                    </div>
                    """, unsafe_allow_html=True)

# ========== 接收用户输入 ==========
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
                    # ===== 新版本 LangChain 写法 =====
                    from langchain_core.runnables import RunnablePassthrough
                    from langchain_core.output_parsers import StrOutputParser
                    from langchain_core.prompts import ChatPromptTemplate
                    from langchain_deepseek import ChatDeepSeek
                    
                    llm = ChatDeepSeek(
                        model="deepseek-chat",
                        api_key=os.getenv("DEEPSEEK_API_KEY"),
                        temperature=0.3
                    )
                    
                    # 构建提示词模板
                    prompt_template = ChatPromptTemplate.from_template("""
                    请基于以下上下文内容回答问题。如果上下文中没有相关信息，请直接说"文档中没有相关内容"。

                    上下文：
                    {context}

                    问题：{question}

                    回答：
                    """)
                    
                    # 检索相关文档
                    retriever = st.session_state.vectorstore.as_retriever(search_kwargs={"k": 4})
                    docs = retriever.invoke(prompt)
                    
                    # 组合上下文
                    context_text = "\n\n".join([doc.page_content for doc in docs])
                    source_texts = [doc.page_content for doc in docs]
                    
                    # 生成回答
                    chain = (
                        {"context": lambda x: context_text, "question": RunnablePassthrough()}
                        | prompt_template
                        | llm
                        | StrOutputParser()
                    )
                    
                    answer = chain.invoke(prompt)
                    st.write(answer)
                    
                    st.session_state.rag_messages.append({
                        "role": "assistant",
                        "content": answer,
                        "sources": source_texts
                    })
                    
                    if source_texts:
                        with st.expander("📚 查看引用来源"):
                            for i, text in enumerate(source_texts, 1):
                                st.markdown(f"""
                                <div class="source-box">
                                    <strong>来源 {i}</strong><br>
                                    {text[:300]}...
                                </div>
                                """, unsafe_allow_html=True)
                    
                except Exception as e:
                    st.error(f"❌ 查询失败：{e}")