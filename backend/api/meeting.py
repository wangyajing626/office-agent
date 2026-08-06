from fastapi import APIRouter, Depends, File, UploadFile
from pydantic import BaseModel
from openai import OpenAI
import os
import tempfile
import requests
from dotenv import load_dotenv
from core.dependencies import get_current_user

load_dotenv("config/.env")

router = APIRouter(prefix="/api/meeting", tags=["会议纪要"])


class TranscriptRequest(BaseModel):
    text: str


class SummaryRequest(BaseModel):
    transcript: str
    meeting_type: str = "其他"


# ===== 语音转文字（智谱 GLM-ASR）=====
def zhipu_speech_to_text(audio_bytes: bytes) -> str:
    api_key = os.getenv("ZHIPU_API_KEY")
    if not api_key:
        return "❌ 请配置 ZHIPU_API_KEY"

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
            return result.get("text", "")
        else:
            return f"❌ 转写失败：{response.status_code}"
    except Exception as e:
        return f"❌ 请求失败：{str(e)}"


# ===== 上传录音 → 转文字 =====
@router.post("/transcribe")
def transcribe_audio(
    file: UploadFile = File(...),
    user=Depends(get_current_user)
):
    try:
        audio_bytes = file.file.read()

        if len(audio_bytes) > 25 * 1024 * 1024:
            return {"text": "❌ 文件大小超过 25MB 限制"}

        if not file.filename.lower().endswith((".wav", ".mp3")):
            return {"text": "❌ 仅支持 WAV 或 MP3 格式"}

        text = zhipu_speech_to_text(audio_bytes)
        return {"text": text}

    except Exception as e:
        return {"text": f"❌ 处理失败：{str(e)}"}


# ===== 粘贴文本 → 生成纪要 =====
@router.post("/summarize")
def summarize_meeting(
    request: SummaryRequest,
    user=Depends(get_current_user)
):
    try:
        client = OpenAI(
            api_key=os.getenv("DEEPSEEK_API_KEY"),
            base_url="https://api.deepseek.com/v1"
        )

        prompt = f"""
请根据以下会议转写文本，生成一份结构化会议纪要。

会议类型：{request.meeting_type}

转写文本：
{request.transcript}

请按以下格式输出：

📌 会议主题
（一句话概括）

🎯 核心决策
（关键决策，每条用 • 开头）

✅ 待办事项
（格式：负责人 | 任务 | 截止日期）

📝 会议摘要
（200字以内）

📊 参会人员
（从文本中提取）

要求：
1. 直接输出会议纪要，不要添加额外说明
2. 待办事项要具体、可执行
3. 如果信息缺失，标注"待补充"
"""

        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "你是专业的会议纪要整理专家"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )

        return {"summary": response.choices[0].message.content}

    except Exception as e:
        return {"summary": f"❌ 生成失败：{str(e)}"}