"""认证接口：注册、登录、当前用户。"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.deps import get_current_user
from app.core.response import success
from app.models.models import User
from app.schemas.schemas import LoginIn, RegisterIn, TokenOut, UserOut
from app.services import auth_service

router = APIRouter(prefix="/auth", tags=["认证"])


@router.post("/register", summary="注册")
def register(data: RegisterIn, db: Session = Depends(get_db)):
    user = auth_service.register(db, data.username, data.password)
    return success(UserOut.model_validate(user).model_dump(), "注册成功")


@router.post("/login", summary="登录")
def login(data: LoginIn, db: Session = Depends(get_db)):
    token = auth_service.login(db, data.username, data.password)
    db_user = db.query(User).filter(User.username == data.username).first()
    payload = TokenOut(token=token, user=UserOut.model_validate(db_user))
    return success(payload.model_dump(), "登录成功")


@router.get("/me", summary="当前用户")
def me(current_user: User = Depends(get_current_user)):
    return success(UserOut.model_validate(current_user).model_dump())
