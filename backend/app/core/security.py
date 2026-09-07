"""提供密码哈希与校验功能。"""

import bcrypt


def hash_password(plain: str) -> str:
    """使用 bcrypt 随机加盐生成密码哈希。"""

    return bcrypt.hashpw(plain.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    """验证明文密码是否匹配已保存的 bcrypt 哈希。"""

    try:
        return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))
    except ValueError:
        return False
