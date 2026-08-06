from fastapi import APIRouter, Depends
from openai import OpenAI
import os
from dotenv import load_dotenv
from models.schemas import ChatRequest, ChatResponse
from core.dependencies import get_current_user

load_dotenv("config/.env")

router = APIRouter(prefix="/api/chat", tags=["聊天"])

@router.post("/send", response_model=ChatResponse)
def send_message(
    request: ChatRequest,
    user=Depends(get_current_user)
):
    try:
        client = OpenAI(
            api_key=os.getenv("DEEPSEEK_API_KEY"),
            base_url="https://api.deepseek.com/v1"
        )

        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": f"你是智能办公助手，当前用户是 {user['sub']}"},
                {"role": "user", "content": request.message}
            ],
            temperature=0.7
        )

        reply = response.choices[0].message.content
        return ChatResponse(reply=reply)

    except Exception as e:
        return ChatResponse(reply=f"AI 调用失败：{str(e)}")