"""用例管理：手工创建 + AI 生成（生成结果先返回给前端确认，不直接入库）。"""
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.deps import get_current_user
from app.core.response import success
from app.models.models import Case, User
from app.schemas.schemas import CaseIn, CaseOut
from app.services import ai_service
from app.services.access import get_api, get_case

router = APIRouter(prefix="/cases", tags=["用例"])


class AiGenerateIn(BaseModel):
    api_id: int
    limit: int = 5


@router.get("", summary="用例列表（按接口过滤）")
def list_cases(api_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    get_api(db, user, api_id)
    rows = db.query(Case).filter(Case.api_id == api_id).order_by(Case.id.desc()).all()
    return success([CaseOut.model_validate(r).model_dump() for r in rows])


@router.post("", summary="新建用例")
def create_case(data: CaseIn, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    get_api(db, user, data.api_id)
    case = Case(**data.model_dump())
    db.add(case)
    db.commit()
    db.refresh(case)
    return success(CaseOut.model_validate(case).model_dump(), "创建成功")


@router.put("/{case_id}", summary="更新用例")
def update_case(case_id: int, data: CaseIn, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    case = get_case(db, user, case_id)
    for key, value in data.model_dump().items():
        setattr(case, key, value)
    db.commit()
    db.refresh(case)
    return success(CaseOut.model_validate(case).model_dump(), "更新成功")


@router.delete("/{case_id}", summary="删除用例")
def delete_case(case_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    case = get_case(db, user, case_id)
    db.delete(case)
    db.commit()
    return success(None, "删除成功")


@router.post("/ai-generate", summary="AI 生成用例（仅返回建议，不入库）")
def ai_generate(data: AiGenerateIn, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    api = get_api(db, user, data.api_id)
    candidates = ai_service.generate_cases(api, limit=data.limit)
    return success(candidates, f"已生成 {len(candidates)} 条建议用例")
