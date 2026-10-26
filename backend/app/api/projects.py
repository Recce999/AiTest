"""项目接口：增删改查，全部限制在当前登录用户范围内。"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.deps import get_current_user
from app.core.response import success
from app.models.models import Project, User
from app.schemas.schemas import ProjectIn, ProjectOut
from app.services.access import get_project

router = APIRouter(prefix="/projects", tags=["项目"])


@router.get("", summary="项目列表")
def list_projects(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    rows = (
        db.query(Project)
        .filter(Project.user_id == user.id)
        .order_by(Project.id.desc())
        .all()
    )
    return success([ProjectOut.model_validate(r).model_dump() for r in rows])


@router.post("", summary="新建项目")
def create_project(data: ProjectIn, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    project = Project(user_id=user.id, **data.model_dump())
    db.add(project)
    db.commit()
    db.refresh(project)
    return success(ProjectOut.model_validate(project).model_dump(), "创建成功")


@router.put("/{project_id}", summary="更新项目")
def update_project(
    project_id: int, data: ProjectIn, db: Session = Depends(get_db), user: User = Depends(get_current_user)
):
    project = get_project(db, user, project_id)
    for key, value in data.model_dump().items():
        setattr(project, key, value)
    db.commit()
    db.refresh(project)
    return success(ProjectOut.model_validate(project).model_dump(), "更新成功")


@router.delete("/{project_id}", summary="删除项目")
def delete_project(project_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    project = get_project(db, user, project_id)
    db.delete(project)
    db.commit()
    return success(None, "删除成功")
