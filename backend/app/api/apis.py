"""接口管理：一个项目下挂多个接口定义。"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.deps import get_current_user
from app.core.response import success
from app.models.models import Api, User
from app.schemas.schemas import ApiIn, ApiOut
from app.services.access import get_api, get_project

router = APIRouter(prefix="/apis", tags=["接口"])


@router.get("", summary="接口列表（按项目过滤）")
def list_apis(
    project_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)
):
    get_project(db, user, project_id)  # 只校验归属，不返回数据
    rows = db.query(Api).filter(Api.project_id == project_id).order_by(Api.id.desc()).all()
    return success([ApiOut.model_validate(r).model_dump() for r in rows])


@router.post("", summary="新建接口")
def create_api(data: ApiIn, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    get_project(db, user, data.project_id)
    api = Api(**data.model_dump())
    db.add(api)
    db.commit()
    db.refresh(api)
    return success(ApiOut.model_validate(api).model_dump(), "创建成功")


@router.put("/{api_id}", summary="更新接口")
def update_api(api_id: int, data: ApiIn, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    api = get_api(db, user, api_id)
    get_project(db, user, data.project_id)
    for key, value in data.model_dump().items():
        setattr(api, key, value)
    db.commit()
    db.refresh(api)
    return success(ApiOut.model_validate(api).model_dump(), "更新成功")


@router.delete("/{api_id}", summary="删除接口")
def delete_api(api_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    api = get_api(db, user, api_id)
    db.delete(api)
    db.commit()
    return success(None, "删除成功")
