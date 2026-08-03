import streamlit as st
from openai import OpenAI
import os
from dotenv import load_dotenv
import smtplib
from email.mime.text import MIMEText
from email.header import Header

# ========== 页面配置 ==========
load_dotenv("config/.env")

st.set_page_config(
    page_title="邮件助手",
    page_icon="📧",
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
    .email-preview {
        background-color: #f8f9fa;
        border-radius: 12px;
        padding: 1.5rem 2rem;
        border-left: 4px solid #667eea;
        font-family: 'Microsoft YaHei', sans-serif;
        line-height: 1.8;
        white-space: pre-wrap;
        min-height: 200px;
    }
    .email-edit-area {
        border-radius: 12px !important;
        border: 2px solid #667eea !important;
        background-color: #fafcff !important;
        font-family: 'Microsoft YaHei', sans-serif !important;
        line-height: 1.8 !important;
        min-height: 200px !important;
    }
    .email-edit-area:focus {
        border-color: #764ba2 !important;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.2) !important;
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
    .stButton button:disabled {
        opacity: 0.5 !important;
        cursor: not-allowed !important;
        transform: none !important;
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
    .stTextInput input {
        border-radius: 12px !important;
        border: 2px solid #e2e8f0 !important;
        transition: all 0.3s ease !important;
    }
    .stTextInput input:focus {
        border-color: #667eea !important;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.2) !important;
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 8px;
        padding: 0.75rem 1rem;
        color: #155724;
    }
    .error-box {
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        border-radius: 8px;
        padding: 0.75rem 1rem;
        color: #721c24;
    }
</style>
""", unsafe_allow_html=True)

# ========== 标题 ==========
st.markdown('<div class="main-title">📧 邮件助手</div>', unsafe_allow_html=True)
st.caption("✍️ 专业邮件撰写 · 一键润色 · 直接编辑 · 真实发送")

st.markdown("---")

# ========== 初始化 ==========
if "email_result" not in st.session_state:
    st.session_state.email_result = ""

if "email_subject" not in st.session_state:
    st.session_state.email_subject = ""

if "is_editing" not in st.session_state:
    st.session_state.is_editing = False

if "edited_content" not in st.session_state:
    st.session_state.edited_content = ""

# ========== 模式选择 ==========
mode = st.radio(
    "选择功能",
    ["✍️ 写邮件", "✨ 润色邮件"],
    horizontal=True
)

st.markdown("---")

# ========== 真实邮件发送函数 ==========
def send_real_email(to_email, subject, content):
    """
    真实发送邮件（使用SMTP）
    """
    # ===== 只需要改这一行 =====
    auth_code = "你的16位授权码"          # ← 改成你的QQ邮箱授权码
    # ===========================
    
    sender = "1625389227@qq.com"
    smtp_server = "smtp.qq.com"
    smtp_port = 465
    
    try:
        # 创建邮件
        msg = MIMEText(content, "plain", "utf-8")
        msg["From"] = sender
        msg["To"] = to_email
        msg["Subject"] = Header(subject, "utf-8")
        
        # 发送
        server = smtplib.SMTP_SSL(smtp_server, smtp_port, timeout=10)
        server.login(sender, auth_code)
        server.sendmail(sender, [to_email], msg.as_string())
        server.quit()
        
        return True, f"✅ 邮件已成功发送至 {to_email}"
        
    except Exception as e:
        return False, f"❌ 发送失败：{str(e)}"

def send_mock_email(to_email, subject, content):
    import time
    time.sleep(0.5)
    return True, f"✅ [模拟] 邮件已发送至 {to_email}"

# ========== 模式一：写邮件 ==========
if mode == "✍️ 写邮件":
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        recipient = st.text_input("📌 收件人", placeholder="请输入收件人姓名或邮箱", key="recipient")
        subject = st.text_input("📌 主题", placeholder="请输入邮件主题", key="subject")
    
    with col2:
        tone = st.selectbox(
            "📌 语气风格",
            ["正式商务", "礼貌友好", "简洁高效"],
            key="tone"
        )
        urgency = st.selectbox(
            "📌 紧急程度",
            ["正常", "紧急", "非紧急"],
            key="urgency"
        )
    
    key_points = st.text_area(
        "📌 邮件要点",
        placeholder="请逐条输入邮件要点，每行一条\n\n例如：\n申请下周三休假一天\n手头工作已交接完毕\n手机保持畅通",
        height=150,
        key="key_points"
    )
    
    col1, col2, col3 = st.columns([1, 1, 3])
    with col1:
        generate_btn = st.button("📝 生成邮件", use_container_width=True)
    
    if generate_btn:
        if not recipient or not subject or not key_points:
            st.warning("⚠️ 请填写收件人、主题和邮件要点")
        else:
            with st.spinner("✍️ 正在撰写邮件..."):
                try:
                    client = OpenAI(
                        api_key=os.getenv("DEEPSEEK_API_KEY"),
                        base_url="https://api.deepseek.com/v1"
                    )
                    
                    tone_prompts = {
                        "正式商务": "语气正式、专业、规范，使用商务邮件的标准用语",
                        "礼貌友好": "语气礼貌、温和、友善，保持专业但更加亲切",
                        "简洁高效": "语气简洁、直接、高效，重点突出，避免冗长"
                    }
                    
                    urgency_prompts = {
                        "正常": "正常处理，按常规时间回复",
                        "紧急": "请务必强调事情的紧急性，需要尽快处理",
                        "非紧急": "强调事情不急，可以安排在合适时间处理"
                    }
                    
                    prompt = f"""
请根据以下信息撰写一封正式的商务邮件：

收件人：{recipient}
主题：{subject}
邮件要点：
{key_points}

写作要求：
1. 风格：{tone_prompts[tone]}
2. 紧急程度：{urgency_prompts[urgency]}
3. 邮件结构：称呼 → 正文 → 结束语 → 署名
4. 直接输出邮件正文，不要包含"主题"、"收件人"等元信息
5. 不要有多余的解释或说明
"""
                    
                    response = client.chat.completions.create(
                        model="deepseek-chat",
                        messages=[
                            {"role": "system", "content": "你是一位专业的商务邮件撰写专家，擅长各种风格的邮件写作。"},
                            {"role": "user", "content": prompt}
                        ],
                        temperature=0.7
                    )
                    
                    st.session_state.email_result = response.choices[0].message.content
                    st.session_state.email_subject = subject
                    st.session_state.is_editing = False
                    st.session_state.edited_content = ""
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"❌ 生成失败：{e}")

# ========== 模式二：润色邮件 ==========
else:
    
    st.info("💡 将您的邮件草稿粘贴到下方，AI将为您润色优化")
    
    draft = st.text_area(
        "📝 邮件草稿",
        placeholder="请在此粘贴您的邮件草稿...",
        height=200,
        key="draft"
    )
    
    col1, col2, col3 = st.columns([1, 1, 3])
    with col1:
        polish_btn = st.button("✨ 润色邮件", use_container_width=True)
    
    if polish_btn:
        if not draft:
            st.warning("⚠️ 请先输入邮件草稿")
        else:
            with st.spinner("✨ 正在润色邮件..."):
                try:
                    client = OpenAI(
                        api_key=os.getenv("DEEPSEEK_API_KEY"),
                        base_url="https://api.deepseek.com/v1"
                    )
                    
                    prompt = f"""
请对以下邮件草稿进行润色优化：

草稿：
{draft}

润色要求：
1. 保持原意不变，不要改变核心内容
2. 修正语法错误和用词不当
3. 让语气更加正式、专业、礼貌
4. 优化邮件结构，使逻辑更清晰
5. 保持适度的亲切感，不要过于生硬
6. 直接输出润色后的完整邮件，不要添加任何解释
"""
                    
                    response = client.chat.completions.create(
                        model="deepseek-chat",
                        messages=[
                            {"role": "system", "content": "你是一位专业的商务邮件润色专家，擅长优化邮件语气和表达。"},
                            {"role": "user", "content": prompt}
                        ],
                        temperature=0.5
                    )
                    
                    st.session_state.email_result = response.choices[0].message.content
                    st.session_state.is_editing = False
                    st.session_state.edited_content = ""
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"❌ 润色失败：{e}")

# ========== 显示结果 ==========
if st.session_state.email_result:
    st.markdown("---")
    
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        st.subheader("📄 邮件预览")
    with col2:
        if not st.session_state.is_editing:
            if st.button("✏️ 编辑内容", use_container_width=True):
                st.session_state.is_editing = True
                st.session_state.edited_content = st.session_state.email_result
                st.rerun()
        else:
            if st.button("👁️ 预览模式", use_container_width=True):
                st.session_state.is_editing = False
                st.rerun()
    with col3:
        if st.button("🗑️ 清空", use_container_width=True):
            st.session_state.email_result = ""
            st.session_state.is_editing = False
            st.session_state.edited_content = ""
            st.rerun()
    
    if st.session_state.is_editing:
        st.caption("✏️ 直接编辑邮件内容，修改后点击下方「保存修改」")
        
        edited_content = st.text_area(
            "邮件内容",
            value=st.session_state.edited_content if st.session_state.edited_content else st.session_state.email_result,
            height=300,
            key="email_editor",
            label_visibility="collapsed"
        )
        
        col1, col2, col3 = st.columns([1, 1, 3])
        with col1:
            if st.button("💾 保存修改", use_container_width=True):
                if edited_content.strip():
                    st.session_state.email_result = edited_content
                    st.session_state.is_editing = False
                    st.session_state.edited_content = ""
                    st.success("✅ 修改已保存！")
                    st.rerun()
                else:
                    st.warning("⚠️ 邮件内容不能为空")
        with col2:
            if st.button("↩️ 放弃修改", use_container_width=True):
                st.session_state.is_editing = False
                st.session_state.edited_content = ""
                st.rerun()
    
    else:
        st.markdown(f"""
        <div class="email-preview">
            {st.session_state.email_result}
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.subheader("📤 发送邮件")
    
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        send_to = st.text_input(
            "收件人邮箱",
            placeholder="请输入对方邮箱地址，如：zhangsan@company.com",
            key="send_to",
            label_visibility="collapsed"
        )
    
    with col2:
        send_mode = st.selectbox(
            "发送模式",
            ["模拟发送", "真实发送"],
            key="send_mode",
            label_visibility="collapsed"
        )
    
    with col3:
        send_btn = st.button("📧 发送邮件", use_container_width=True)
    
    if send_mode == "真实发送":
        st.caption("⚠️ 真实发送需要配置邮箱授权码，当前为演示模式")
    
    if send_btn:
        if not send_to:
            st.warning("⚠️ 请填写收件人邮箱地址")
        else:
            if "@" not in send_to or "." not in send_to:
                st.warning("⚠️ 请输入正确的邮箱格式（如：xxx@qq.com）")
            else:
                if send_mode == "模拟发送":
                    success, msg = send_mock_email(send_to, st.session_state.email_subject, st.session_state.email_result)
                else:
                    success, msg = send_real_email(send_to, st.session_state.email_subject, st.session_state.email_result)
                
                if success:
                    st.markdown(f'<div class="success-box">{msg}</div>', unsafe_allow_html=True)
                    st.balloons()
                else:
                    st.markdown(f'<div class="error-box">{msg}</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 1, 3])
    with col1:
        if st.button("📋 复制内容", use_container_width=True):
            st.write("📋 已复制到剪贴板")
    with col2:
        if st.button("🔄 重新生成", use_container_width=True):
            st.session_state.email_result = ""
            st.session_state.is_editing = False
            st.session_state.edited_content = ""
            st.rerun()