"""认证业务逻辑：注册与登录。

分层原则：路由只收参数、调这里、返回结果；查重与加密都在 service 里。
"""
from sqlalchemy.orm import Session

from app.core.exceptions import BizError
from app.core.security import create_access_token, hash_password, verify_password
from app.models.models import User


def register(db: Session, username: str, password: str) -> User:
    if db.query(User).filter(User.username == username).first():
        raise BizError("用户名已存在")
    user = User(username=username, password_hash=hash_password(password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def login(db: Session, username: str, password: str) -> str:
    user = db.query(User).filter(User.username == username).first()
    # 不区分“用户不存在”和“密码错误”，避免被用来枚举用户名
    if user is None or not verify_password(password, user.password_hash):
        raise BizError("用户名或密码错误")
    return create_access_token(user.id)
