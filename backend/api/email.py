from fastapi import APIRouter, Depends
from pydantic import BaseModel
from openai import OpenAI
import os
from dotenv import load_dotenv
from core.dependencies import get_current_user

load_dotenv("config/.env")

router = APIRouter(prefix="/api/email", tags=["邮件"])

# ===== 请求体格式 =====
class EmailRequest(BaseModel):
    recipient: str
    subject: str
    key_points: str
    tone: str = "正式商务"
    urgency: str = "正常"

# ===== 响应体格式 =====
class EmailResponse(BaseModel):
    email: str

# ===== 生成邮件接口 =====
@router.post("/generate", response_model=EmailResponse)
def generate_email(
    request: EmailRequest,
    user=Depends(get_current_user)
):
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

收件人：{request.recipient}
主题：{request.subject}
邮件要点：
{request.key_points}

写作要求：
1. 风格：{tone_prompts.get(request.tone, '正式商务')}
2. 紧急程度：{urgency_prompts.get(request.urgency, '正常')}
3. 邮件结构：称呼 → 正文 → 结束语 → 署名
4. 直接输出邮件正文，不要包含任何额外说明
"""

        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": f"你是专业的商务邮件撰写专家，当前用户是 {user['sub']}"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )

        email_content = response.choices[0].message.content
        return EmailResponse(email=email_content)

    except Exception as e:
        return EmailResponse(email=f"生成失败：{str(e)}")