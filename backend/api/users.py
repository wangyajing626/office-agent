from fastapi import APIRouter, HTTPException
from models.schemas import UserRegister, UserResponse, UserLogin
from services.user_service import register_user, login_user
from core.auth import create_access_token

router = APIRouter(prefix="/api/users", tags=["用户管理"])

@router.post("/register", response_model=UserResponse)
def register(user: UserRegister):
    success, user_id, message = register_user(user.username, user.password)
    if not success:
        raise HTTPException(status_code=400, detail=message)
    return UserResponse(id=user_id, username=user.username, message=message)

@router.post("/login")
def login(user: UserLogin):
    success, user_data, message = login_user(user.username, user.password)
    if not success:
        raise HTTPException(status_code=400, detail=message)

    token = create_access_token({"sub": user_data["username"], "id": user_data["id"]})

    return {
        "id": user_data["id"],
        "username": user_data["username"],
        "token": token,
        "message": "登录成功"
    }