# 缺陷记录

记录开发与自测过程中发现并修复的真实缺陷。每条包含：现象、复现方式、根因、修复、验证、可迁移的经验。

---

## BUG-001 删除项目后执行记录变成孤儿数据

| 项目 | 内容 |
|---|---|
| 发现时间 | 2026-10-26 |
| 发现方式 | 端到端实测（走真实 HTTP 接口验证全流程，而非单元测试） |
| 严重级别 | 中（不崩溃，但数据会持续堆积且无法通过界面清理） |
| 影响版本 | 修复前所有版本 |
| 修复提交 | `a3afcc7` |

### 现象

删除一个项目之后，该项目下的接口和用例都被清理了，但它的测试报告（执行记录与执行明细）仍然留在数据库里。

这些残留数据无法通过界面再访问到——它们指向一个已经不存在的项目，前端查不到入口。结果是数据库只增不减：每删一次有历史报告的项目，就永久多出一批读不到也删不掉的记录。

### 复现步骤

1. 建一个项目，在它下面建接口和用例
2. 执行一次，产生一条执行记录和若干条执行明细
3. 删除这个项目
4. 查数据库：执行记录和执行明细的条数没有变化

### 根因

删除项目走的是 ORM 级联：

```python
# 修复前
db.delete(project)
db.commit()
```

而 `cascade="all, delete-orphan"` 只配置在两条关系上：

```python
# app/models/models.py
class Project(Base):
    apis: Mapped[list["Api"]] = relationship(
        back_populates="project", cascade="all, delete-orphan"
    )

class Api(Base):
    cases: Mapped[list["Case"]] = relationship(
        back_populates="api", cascade="all, delete-orphan"
    )
```

`Run` 和 `RunResult` 只有外键字段，**没有定义任何 relationship**：

```python
class Run(Base):
    __tablename__ = "runs"
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"), index=True)

class RunResult(Base):
    __tablename__ = "run_results"
    run_id: Mapped[int] = mapped_column(ForeignKey("runs.id"), index=True)
```

**关键点：ORM 级联只在「配置了 relationship 的方向」生效。** 只写外键不写 relationship，数据库层虽然有外键约束，但 SQLAlchemy 不会替你去级联删除；而 SQLite 默认不开启外键约束检查（`PRAGMA foreign_keys` 默认关闭），所以连数据库层面的阻止也没有——删除直接成功，数据静静变成孤儿。

### 修复

在删除项目前显式清理执行记录与明细：

```python
# app/api/projects.py
@router.delete("/{project_id}", summary="删除项目")
def delete_project(project_id: int, db: Session = Depends(get_db),
                   user: User = Depends(get_current_user)):
    project = get_project(db, user, project_id)
    # 接口和用例靠 ORM 关系级联删除；
    # 执行记录与执行结果没配关系，必须显式清理，否则留下孤儿数据
    run_ids = [row[0] for row in db.query(Run.id).filter(Run.project_id == project.id)]
    if run_ids:
        db.query(RunResult).filter(RunResult.run_id.in_(run_ids)).delete(
            synchronize_session=False
        )
        db.query(Run).filter(Run.id.in_(run_ids)).delete(synchronize_session=False)
    db.delete(project)
    db.commit()
    return success(None, "删除成功")
```

先删明细再删记录，顺序不能反——明细通过 `run_id` 指向记录，反过来会留下指向已删记录的明细。

### 为什么选择显式删除，而不是补 ORM 关系

补关系需要同时改两个模型：给 `Run` 加 `project` 反向引用、给 `Run` 加 `results` 关系，还要给 `Project` 加 `runs` 关系并配级联。改动面大，且会把「什么时候清理报告」这个业务决定埋进模型声明里。

报告是历史证据，保留多久、什么时候清，属于业务规则而不是数据结构。放在删除逻辑里写清楚，意图更直白，也不会影响其他查询路径。

### 验证

1. **新增回归测试** `test_delete_project_purges_run_history`：建项目 → 建接口 → 建用例 → 执行 → 删项目 → 断言执行记录和明细都已不存在。pytest 全部 26 个用例通过。
2. **真实接口验证**：重启服务后，用 HTTP 请求把同样的流程走一遍，再直接查 SQLite 确认：
   - 该批次记录 → 已清除
   - 该批次明细条数 → 0
   - 该项目接口条数 → 0
   - 全局孤儿执行记录 → 0

### 经验

- **单元测试覆盖不到这类问题。** 原来的 `test_update_and_delete` 只断言「项目列表变空了」，而孤儿数据在另一张表里，测试看不见。是端到端实测（走真实 HTTP、再回头看数据库）才暴露出来的。
- **删数据要验证「所有关联表」，不能只看主表。** 删除类操作的自测清单应该是：主表记录、一对多子表、跨层级孙表，逐个确认。
- **SQLite 不默认校验外键。** 开发期用 SQLite 时，即使写了 `ForeignKey` 也可能被违规数据悄悄污染；换到 PostgreSQL 会直接报错，那时问题会在生产暴露。要么开启 `PRAGMA foreign_keys=ON`，要么在应用层把清理逻辑写全。
- **级联删除是「配置了的才生效」，不是「有外键就生效」。** 这个认知差是本次缺陷的直接来源。

### 面试可用的讲法

> 我在做端到端实测时发现，删项目之后测试报告没有被一起清掉。查下来是因为 ORM 的级联删除只在配置了 relationship 的方向生效——`Project.apis` 和 `Api.cases` 配了级联，但 `Run` 只有外键字段、没有定义关系，所以不会被连带删除；加上 SQLite 默认不校验外键，删除就这样静默成功了。
>
> 修复是在删除项目前显式清理执行记录和明细，先删明细再删记录。同时补了一个回归测试，断言删完项目之后执行记录和明细都查不到。
>
> 这件事让我意识到两件事：一是删除操作的自测要覆盖所有关联表，不能只看主表；二是开发期用的数据库如果比生产宽松（SQLite 不校验外键），本地测得过不代表生产没问题。
