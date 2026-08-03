import streamlit as st
from openai import OpenAI
import os
from dotenv import load_dotenv
from datetime import datetime

# ========== 页面配置 ==========
load_dotenv("config/.env")

st.set_page_config(
    page_title="智能对话",
    page_icon="💬",
    layout="wide"
)

# ========== 自定义CSS样式（统一字体大小） ==========
st.markdown("""
<style>
    /* 标题样式 */
    .main-title {
        font-size: 2.2rem;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        padding: 0.5rem 0;
    }
    
    /* 侧边栏样式 */
    .sidebar-header {
        font-size: 1.2rem;
        font-weight: 600;
        color: #4a5568;
        padding: 0.5rem 0;
        border-bottom: 2px solid #e2e8f0;
        margin-bottom: 1rem;
    }
    
    /* 消息气泡优化 */
    .stChatMessage {
        border-radius: 12px !important;
        padding: 0.5rem 1rem !important;
    }
    
    /* 用户消息背景 */
    .stChatMessage [data-testid="stChatMessageContent"] {
        background-color: #667eea !important;
        color: white !important;
        border-radius: 12px 12px 4px 12px !important;
        padding: 0.75rem 1rem !important;
    }
    
    /* AI消息背景 */
    .stChatMessage [data-testid="stChatMessageContent"]:has(.stMarkdown) {
        background-color: #f7fafc !important;
        color: #2d3748 !important;
        border-radius: 12px 12px 12px 4px !important;
        padding: 0.75rem 1rem !important;
        border: 1px solid #e2e8f0 !important;
    }
    
    /* ===== 统一字体大小：AI回复里的所有文字都一样大 ===== */
    .stChatMessage p,
    .stChatMessage li,
    .stChatMessage h1,
    .stChatMessage h2,
    .stChatMessage h3,
    .stChatMessage h4,
    .stChatMessage h5,
    .stChatMessage h6,
    .stChatMessage strong,
    .stChatMessage em,
    .stChatMessage span,
    .stChatMessage div,
    .stMarkdown p,
    .stMarkdown li,
    .stMarkdown h1,
    .stMarkdown h2,
    .stMarkdown h3,
    .stMarkdown h4,
    .stMarkdown h5,
    .stMarkdown h6 {
        font-size: 1rem !important;
        line-height: 1.8 !important;
    }
    
    /* 列表缩进调整 */
    .stChatMessage ul,
    .stChatMessage ol {
        padding-left: 1.5rem !important;
        margin: 0.25rem 0 !important;
    }
    
    /* 段落间距 */
    .stChatMessage p {
        margin-bottom: 0.5rem !important;
    }
    
    /* 代码字体稍小一点（保持可读性） */
    .stChatMessage code,
    .stChatMessage pre,
    .stChatMessage pre code {
        font-size: 0.9rem !important;
        line-height: 1.6 !important;
    }
    
    .stChatMessage pre {
        background-color: #1a202c !important;
        color: #e2e8f0 !important;
        padding: 0.75rem !important;
        border-radius: 8px !important;
        overflow-x: auto !important;
    }
    
    .stChatMessage pre code {
        background-color: transparent !important;
        color: #e2e8f0 !important;
        padding: 0 !important;
    }
    
    /* 引用块 */
    .stChatMessage blockquote {
        font-size: 1rem !important;
        border-left: 4px solid #667eea !important;
        padding-left: 1rem !important;
        margin: 0.5rem 0 !important;
        color: #4a5568 !important;
    }
    /* ===== 统一字体大小结束 ===== */
    
    /* 输入框美化 */
    .stChatInputContainer {
        border-top: 2px solid #e2e8f0 !important;
        padding-top: 1rem !important;
    }
    
    .stChatInputContainer textarea {
        border-radius: 20px !important;
        border: 2px solid #e2e8f0 !important;
        padding: 0.75rem 1.5rem !important;
        font-size: 1rem !important;
        transition: all 0.3s ease !important;
    }
    
    .stChatInputContainer textarea:focus {
        border-color: #667eea !important;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.2) !important;
    }
    
    /* 按钮美化 */
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
    
    /* 统计信息卡片 */
    .stats-card {
        background: linear-gradient(135deg, #f7fafc 0%, #edf2f7 100%);
        border-radius: 12px;
        padding: 0.75rem 1rem;
        border: 1px solid #e2e8f0;
        margin: 0.25rem 0;
    }
    
    /* 消息动画 */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .stChatMessage {
        animation: fadeIn 0.3s ease-out;
    }
</style>
""", unsafe_allow_html=True)

# ========== 侧边栏 ==========
with st.sidebar:
    st.markdown('<div class="sidebar-header">🤖 智能助手</div>', unsafe_allow_html=True)
    
    # 显示当前日期
    today = datetime.now().strftime("%Y年%m月%d日")
    weekday = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"][datetime.now().weekday()]
    st.info(f"📅 {today} {weekday}")
    
    st.markdown("---")
    
    # 清空按钮
    if st.button("🗑️ 清空对话", use_container_width=True):
        st.session_state.messages = [
            {"role": "system", "content": f"今天是{today} {weekday}，你是一个专业的办公助理，请用中文回答用户的问题。"}
        ]
        st.rerun()
    
    st.markdown("---")
    
    # 设置区
    with st.expander("⚙️ 高级设置"):
        temperature = st.slider(
            "创意度",
            min_value=0.0,
            max_value=1.0,
            value=0.7,
            step=0.1,
            help="数值越高，回答越有创意；数值越低，回答越稳定"
        )
        st.session_state.temperature = temperature
    
    st.markdown("---")
    
    # 模型信息
    st.caption("🚀 驱动模型：DeepSeek Chat")

# ========== 主页面 ==========
# 标题
st.markdown('<div class="main-title">💬 智能对话助手</div>', unsafe_allow_html=True)
st.caption("✨ 随时提问，随时解答 — 你的专属AI办公助理")

st.markdown("---")

# ========== 初始化聊天历史 ==========
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": f"今天是{today} {weekday}，你是一个专业的办公助理，请用中文回答用户的问题。"}
    ]

if "temperature" not in st.session_state:
    st.session_state.temperature = 0.7

# ========== 显示历史消息 ==========
for msg in st.session_state.messages:
    if msg["role"] != "system":
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

# ========== 接收用户输入 ==========
if prompt := st.chat_input("💭 输入你的问题..."):
    # 显示用户消息
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)
    
    # 调用AI
    with st.chat_message("assistant"):
        with st.spinner("🤔 思考中..."):
            try:
                client = OpenAI(
                    api_key=os.getenv("DEEPSEEK_API_KEY"),
                    base_url="https://api.deepseek.com/v1"
                )
                
                response = client.chat.completions.create(
                    model="deepseek-chat",
                    messages=st.session_state.messages,
                    temperature=st.session_state.temperature
                )
                
                reply = response.choices[0].message.content
                st.write(reply)
                st.session_state.messages.append({"role": "assistant", "content": reply})
                
            except Exception as e:
                st.error(f"❌ 调用 AI 失败：{e}")