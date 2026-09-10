"""提供用户认证相关的 HTTP 路由。"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.auth import LoginIn, LoginOut, RegisterIn, RegisterOut
from app.schemas.user import UserOut
from app.services.auth_service import InvalidCredentialsError, login
from app.services.user_service import UserAlreadyExistsError, register

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=RegisterOut, status_code=status.HTTP_201_CREATED)
def register_user(data: RegisterIn, db: Session = Depends(get_db)) -> RegisterOut:
    """接收注册参数并组装 HTTP 响应。"""

    try:
        return register(db, data)
    except UserAlreadyExistsError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc


@router.post("/login", response_model=LoginOut)
def login_user(data: LoginIn, db: Session = Depends(get_db)) -> LoginOut:
    """验证登录信息并组装访问令牌响应。"""

    try:
        access_token = login(db, data)
    except InvalidCredentialsError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
        ) from exc

    return LoginOut(
        access_token=access_token,
        expires_in=settings.access_token_expire_minutes * 60,
    )


@router.get("/me", response_model=UserOut)
def read_current_user(
    current_user: Annotated[User, Depends(get_current_user)],
) -> UserOut:
    """返回当前登录用户的公开资料。"""

    return current_user
