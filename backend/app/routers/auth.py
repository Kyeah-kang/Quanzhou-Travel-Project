"""提供用户认证相关的 HTTP 路由。"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.auth import RegisterIn, RegisterOut
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
