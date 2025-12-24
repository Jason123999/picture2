from __future__ import annotations

from typing import List

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.api.deps import get_current_tenant, get_current_user, get_db_session
from app.models import ImageAsset, ProcessingTask, Tenant, User
from app.models.processing_task import TaskStatus
from app.schemas.task import TaskCreate, TaskRead, TaskUpdate
from app.services.tasks import execute_processing_task

router = APIRouter()


@router.post("/", response_model=TaskRead, status_code=status.HTTP_202_ACCEPTED)
async def create_task(
    payload: TaskCreate,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_db_session),
    tenant: Tenant = Depends(get_current_tenant),
    user: User = Depends(get_current_user),
) -> TaskRead:
    if payload.tenant_id != tenant.id:
        raise HTTPException(status_code=403, detail="Invalid tenant scope")

    asset = await session.get(ImageAsset, payload.image_asset_id)
    if asset is None or asset.tenant_id != tenant.id:
        raise HTTPException(status_code=404, detail="Image asset not found for tenant")

    task = ProcessingTask(
        tenant_id=tenant.id,
        image_asset_id=payload.image_asset_id,
        config_path=payload.config_path,
        output_dir=payload.output_dir,
        status=TaskStatus.PENDING,
    )
    session.add(task)
    await session.commit()
    await session.refresh(task)

    background_tasks.add_task(process_task_job, task.id)

    return TaskRead.model_validate(task)


@router.get("/", response_model=List[TaskRead])
async def list_tasks(
    session: AsyncSession = Depends(get_db_session),
    tenant: Tenant = Depends(get_current_tenant),
) -> List[TaskRead]:
    result = await session.exec(
        select(ProcessingTask).where(ProcessingTask.tenant_id == tenant.id)
    )
    tasks = result.all()
    return [TaskRead.model_validate(task) for task in tasks]


@router.get("/{task_id}", response_model=TaskRead)
async def get_task(
    task_id: int,
    session: AsyncSession = Depends(get_db_session),
    tenant: Tenant = Depends(get_current_tenant),
) -> TaskRead:
    task = await session.get(ProcessingTask, task_id)
    if task is None or task.tenant_id != tenant.id:
        raise HTTPException(status_code=404, detail="Task not found")
    return TaskRead.model_validate(task)


@router.patch("/{task_id}", response_model=TaskRead)
async def update_task(
    task_id: int,
    payload: TaskUpdate,
    session: AsyncSession = Depends(get_db_session),
    tenant: Tenant = Depends(get_current_tenant),
) -> TaskRead:
    task = await session.get(ProcessingTask, task_id)
    if task is None or task.tenant_id != tenant.id:
        raise HTTPException(status_code=404, detail="Task not found")

    update_data = payload.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(task, key, value)

    await session.commit()
    await session.refresh(task)
    return TaskRead.model_validate(task)


async def process_task_job(task_id: int) -> None:
    from app.db.session import async_session

    async with async_session() as session:  # type: ignore[call-arg]
        task = await session.get(ProcessingTask, task_id)
        if task is None:
            return
        await execute_processing_task(session, task)
