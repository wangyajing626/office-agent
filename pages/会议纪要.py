import streamlit as st
from openai import OpenAI
import os
from dotenv import load_dotenv
from datetime import datetime
import tempfile
import requests

# ========== 页面配置 ==========
load_dotenv("config/.env")

st.set_page_config(
    page_title="会议纪要",
    page_icon="📝",
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
    .meeting-preview {
        background-color: #f8f9fa;
        border-radius: 12px;
        padding: 1.5rem 2rem;
        border-left: 4px solid #667eea;
        font-family: 'Microsoft YaHei', sans-serif;
        line-height: 1.8;
        white-space: pre-wrap;
        min-height: 200px;
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
    .stTextArea textarea {
        border-radius: 12px !important;
        border: 2px solid #e2e8f0 !important;
        transition: all 0.3s ease !important;
    }
    .stTextArea textarea:focus {
        border-color: #667eea !important;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.2) !important;
    }
</style>
""", unsafe_allow_html=True)

# ========== 标题 ==========
st.markdown('<div class="main-title">📝 会议纪要</div>', unsafe_allow_html=True)
st.caption("🎙️ 录音 → 智谱转文字 → AI 整理成结构化会议纪要")

st.markdown("---")

# ========== 初始化 ==========
if "meeting_result" not in st.session_state:
    st.session_state.meeting_result = ""

if "transcript_text" not in st.session_state:
    st.session_state.transcript_text = ""

# ========== 侧边栏 ==========
with st.sidebar:
    st.subheader("⚙️ 会议设置")
    
    meeting_type = st.selectbox(
        "会议类型",
        ["项目评审", "团队周会", "需求评审", "技术方案讨论", "客户会议", "其他"],
        help="选择会议类型，AI 会调整纪要风格"
    )
    
    st.markdown("---")
    
    # 显示 API 状态
    zhipu_key = os.getenv("ZHIPU_API_KEY")
    if zhipu_key:
        st.success("✅ 智谱 API 已配置")
    else:
        st.error("❌ 请配置 ZHIPU_API_KEY")

# ========== 智谱语音转文字函数 ==========
def zhipu_speech_to_text(audio_bytes):
    """调用智谱 GLM-ASR 语音转文字"""
    
    api_key = os.getenv("ZHIPU_API_KEY")
    if not api_key:
        return None, "❌ 请配置 ZHIPU_API_KEY"
    
    url = "https://open.bigmodel.cn/api/paas/v4/audio/transcriptions"
    
    headers = {
        "Authorization": f"Bearer {api_key}"
    }
    
    files = {
        "file": ("audio.wav", audio_bytes, "audio/wav"),
        "model": (None, "glm-asr-2512"),
        "language": (None, "zh")
    }
    
    try:
        response = requests.post(url, headers=headers, files=files, timeout=60)
        if response.status_code == 200:
            result = response.json()
            return result.get("text", ""), None
        else:
            return None, f"❌ 转写失败：{response.status_code} - {response.text}"
    except requests.exceptions.Timeout:
        return None, "❌ 请求超时，请重试"
    except Exception as e:
        return None, f"❌ 请求失败：{e}"

# ========== 主页面 ==========

tab1, tab2 = st.tabs(["🎙️ 录音转文字", "📝 粘贴已有文本"])

# ========== Tab 1: 录音转文字 ==========
with tab1:
    st.subheader("🎙️ 录音并生成纪要")
    st.info("🎤 点击下方按钮录音，智谱 GLM-ASR 转文字，AI 整理成纪要")
    
    audio_value = st.audio_input("点击录音", sample_rate=16000)
    
    if audio_value:
        with st.spinner("🎤 正在使用智谱转写..."):
            audio_bytes = audio_value.getvalue()
            text, error = zhipu_speech_to_text(audio_bytes)
            
            if error:
                st.error(error)
                st.info("💡 请检查 ZHIPU_API_KEY 是否正确，以及账户是否有免费额度")
            else:
                st.success("✅ 智谱转写完成！")
                st.text_area("📝 转写结果（可编辑）", text, height=150, key="transcript_edit")
                st.session_state.transcript_text = text

# ========== Tab 2: 粘贴已有文本 ==========
with tab2:
    st.subheader("📝 粘贴会议转写文本")
    st.caption("如果有现成的会议录音转写文本，可以直接粘贴")
    
    transcript = st.text_area(
        "会议内容",
        placeholder="请粘贴会议转写文本...",
        height=250,
        key="transcript_paste"
    )
    
    if transcript:
        st.session_state.transcript_text = transcript

# ========== 生成会议纪要 ==========
if st.session_state.transcript_text:
    st.markdown("---")
    
    col1, col2 = st.columns([1, 5])
    with col1:
        generate_btn = st.button("🚀 生成纪要", use_container_width=True)
    
    if generate_btn:
        text = st.session_state.transcript_text.strip()
        if len(text) < 20:
            st.warning("⚠️ 内容太短，请提供更多文本")
        else:
            with st.spinner("📝 AI 正在整理会议纪要..."):
                try:
                    client = OpenAI(
                        api_key=os.getenv("DEEPSEEK_API_KEY"),
                        base_url="https://api.deepseek.com/v1"
                    )
                    
                    type_prompts = {
                        "项目评审": "项目评审会议，重点关注项目进度、风险、资源分配",
                        "团队周会": "团队周会，重点关注本周进展、下周计划、遇到的困难",
                        "需求评审": "需求评审会议，重点关注需求理解、技术可行性、排期",
                        "技术方案讨论": "技术方案讨论，重点关注方案选择、技术决策、风险评估",
                        "客户会议": "客户会议，重点关注客户反馈、需求变更、满意度",
                        "其他": "日常工作会议"
                    }
                    
                    prompt = f"""
请根据以下会议转写文本，生成一份结构化会议纪要。

会议类型：{meeting_type}
会议风格：{type_prompts[meeting_type]}

转写文本：
{text}

请按以下格式输出：

📌 会议主题
（一句话概括会议核心主题）

🎯 核心决策
（列出本次会议做出的关键决策，每条用 • 开头）

✅ 待办事项
（格式：负责人 | 具体任务 | 截止日期）
（如果没有明确截止日期，标注"待定"）

📝 会议摘要
（200字以内的会议内容概述）

📊 参会人员
（从文本中提取参会人员名单，提取不到就写"待补充"）

⚠️ 风险/问题
（会议中提到的风险和问题）

要求：
1. 直接输出会议纪要，不要添加额外说明
2. 待办事项要具体、可执行
3. 如果转写文本中缺失某些信息，标注"待补充"
4. 使用 Markdown 格式
"""
                    
                    response = client.chat.completions.create(
                        model="deepseek-chat",
                        messages=[
                            {"role": "system", "content": "你是一位专业的会议纪要整理专家，擅长从转写文本中提取结构化信息。输出格式要清晰、简洁、可读性强。"},
                            {"role": "user", "content": prompt}
                        ],
                        temperature=0.3
                    )
                    
                    st.session_state.meeting_result = response.choices[0].message.content
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"❌ 生成失败：{e}")
                    st.info("💡 请检查 DEEPSEEK_API_KEY 是否正确")

# ========== 显示结果 ==========
if st.session_state.meeting_result:
    st.markdown("---")
    st.subheader("📄 会议纪要")
    
    col1, col2, col3, col4 = st.columns([1, 1, 1, 2])
    with col1:
        if st.button("📋 复制", use_container_width=True):
            st.write("📋 已复制到剪贴板")
    with col2:
        if st.button("🔄 重新生成", use_container_width=True):
            st.session_state.meeting_result = ""
            st.rerun()
    with col3:
        if st.button("🗑️ 清空", use_container_width=True):
            st.session_state.meeting_result = ""
            st.session_state.transcript_text = ""
            st.rerun()
    
    st.markdown(f"""
    <div class="meeting-preview">
        {st.session_state.meeting_result}
    </div>
    """, unsafe_allow_html=True)
    
    st.download_button(
        label="📥 下载 Markdown",
        data=st.session_state.meeting_result,
        file_name=f"会议纪要_{datetime.now().strftime('%Y%m%d_%H%M')}.md",
        mime="text/markdown",
        use_container_width=True
    )