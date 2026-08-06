from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api import users, chat ,email,rag,meeting

app = FastAPI(
    title="Office Agent API",
    description="智能办公助手后端服务",
    version="1.0.0"
)

# 跨域配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 根路径
@app.get("/")
def root():
    return {"message": "Office Agent API 运行中", "status": "ok"}

# 注册用户路由
app.include_router(users.router)
app.include_router(chat.router)
app.include_router(email.router)
app.include_router(rag.router)
app.include_router(meeting.router)