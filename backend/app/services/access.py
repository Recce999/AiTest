"""权限校验：所有查询都必须带 user_id，防止越权访问别人的数据。"""
from sqlalchemy.orm import Session

from app.core.exceptions import BizError
from app.models.models import Api, Case, Project, User


def get_project(db: Session, user: User, project_id: int) -> Project:
    project = db.get(Project, project_id)
    if project is None or project.user_id != user.id:
        # 不区分“不存在”和“不是你的”，避免被枚举 ID
        raise BizError("项目不存在或无权访问", code=403)
    return project


def get_api(db: Session, user: User, api_id: int) -> Api:
    api = db.get(Api, api_id)
    if api is None:
        raise BizError("接口不存在", code=404)
    get_project(db, user, api.project_id)
    return api


def get_case(db: Session, user: User, case_id: int) -> Case:
    case = db.get(Case, case_id)
    if case is None:
        raise BizError("用例不存在", code=404)
    get_api(db, user, case.api_id)
    return case
