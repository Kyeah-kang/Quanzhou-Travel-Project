"""定义用户相关的对外响应模型。"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr


class UserOut(BaseModel):
    """用户公开信息响应，明确排除密码等敏感字段。"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    email: EmailStr | None
    nickname: str | None
    created_at: datetime
