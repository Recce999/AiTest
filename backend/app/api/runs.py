"""执行与报告：一次执行对应 runs 一行 + run_results 多行。"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.deps import get_current_user
from app.core.exceptions import BizError
from app.core.response import success
from app.models.models import Case, Run, RunResult, User
from app.schemas.schemas import RunIn, RunOut, RunResultOut
from app.services.access import get_project
from app.services.executor import execute_run

router = APIRouter(prefix="/runs", tags=["执行"])


@router.post("", summary="触发执行")
def create_run(data: RunIn, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    project = get_project(db, user, data.project_id)

    query = db.query(Case).join(Case.api).filter_by(project_id=project.id).filter(Case.enabled.is_(True))
    if data.case_ids:
        query = query.filter(Case.id.in_(data.case_ids))
    cases = query.all()

    run = execute_run(db, project, cases)
    return success(_to_out(db, run).model_dump(), "执行完成")


@router.get("", summary="执行历史")
def list_runs(project_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    get_project(db, user, project_id)
    rows = db.query(Run).filter(Run.project_id == project_id).order_by(Run.id.desc()).limit(20).all()
    return success(
        [
            {
                "id": r.id,
                "total": r.total,
                "passed": r.passed,
                "failed": r.failed,
                "duration_ms": r.duration_ms,
                "created_at": r.created_at.isoformat(),
            }
            for r in rows
        ]
    )


@router.get("/{run_id}", summary="报告详情")
def get_run(run_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    run = db.get(Run, run_id)
    if run is None:
        raise BizError("执行记录不存在", code=404)
    get_project(db, user, run.project_id)
    return success(_to_out(db, run).model_dump())


def _to_out(db: Session, run: Run) -> RunOut:
    results = db.query(RunResult).filter(RunResult.run_id == run.id).all()
    return RunOut(
        id=run.id,
        total=run.total,
        passed=run.passed,
        failed=run.failed,
        duration_ms=run.duration_ms,
        results=[RunResultOut.model_validate(r) for r in results],
    )
