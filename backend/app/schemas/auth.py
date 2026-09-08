"""定义注册接口的请求与响应模型。"""

from typing import Annotated

from pydantic import BaseModel, EmailStr, Field

from app.schemas.user import UserOut


class RegisterIn(BaseModel):
    """注册请求参数。"""

    username: Annotated[
        str,
        Field(min_length=3, max_length=20, pattern=r"^[A-Za-z0-9_]+$"),
    ]
    email: EmailStr | None = None
    password: Annotated[str, Field(min_length=8)]


RegisterOut = UserOut


class LoginIn(BaseModel):
    """登录请求参数。"""

    username: str
    password: str


class LoginOut(BaseModel):
    """登录成功后返回的访问令牌信息。"""

    access_token: str
    token_type: str = "bearer"
    expires_in: int
