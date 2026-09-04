from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_async_session
from app.core.user import current_superuser
from app.models.charity_project import CharityProject
from app.schemas.charity_project import (
    CharityProjectCreate,
    CharityProjectDB,
    CharityProjectUpdate,
)
from app.services.investing import invest_into_project

router = APIRouter(prefix="/charity_project", tags=["charity_projects"])


async def get_project_or_404(
    project_id: int,
    session: AsyncSession,
) -> CharityProject:
    result = await session.execute(
        select(CharityProject).where(CharityProject.id == project_id)
    )
    project = result.scalars().first()
    if project is None:
        raise HTTPException(status_code=404, detail="Проект не найден.")
    return project


@router.get(
    "/",
    response_model=list[CharityProjectDB],
    description="Показать список всех целевых проектов.",
)
async def get_all_charity_projects(
    session: AsyncSession = Depends(get_async_session),
):
    result = await session.execute(select(CharityProject))
    return result.scalars().all()


@router.post(
    "/",
    response_model=CharityProjectDB,
    description="Создать целевой проект.",
)
async def create_charity_project(
    project: CharityProjectCreate,
    session: AsyncSession = Depends(get_async_session),
    _=Depends(current_superuser),
):
    exists = await session.execute(
        select(CharityProject).where(CharityProject.name == project.name)
    )
    if exists.scalars().first() is not None:
        raise HTTPException(
            status_code=400,
            detail="Проект с таким именем уже существует!",
        )

    db_project = CharityProject(**project.model_dump())
    session.add(db_project)
    await session.flush()

    await invest_into_project(db_project, session)
    await session.commit()
    return db_project


@router.patch(
    "/{project_id}",
    response_model=CharityProjectDB,
    description=(
        "Редактировать целевой проект.\n\n"
        "Закрытый проект нельзя редактировать; "
        "нельзя установить требуемую сумму меньше уже вложенной."
    ),
)
async def update_charity_project(
    project_id: int,
    data: CharityProjectUpdate,
    session: AsyncSession = Depends(get_async_session),
    _=Depends(current_superuser),
):
    project = await get_project_or_404(project_id, session)

    if project.fully_invested:
        raise HTTPException(
            status_code=400,
            detail="Закрытый проект нельзя редактировать!",
        )

    payload = data.model_dump(exclude_unset=True)

    # Проверка уникальности имени (если меняем name)
    if (
        "name" in payload
        and payload["name"] is not None
    ):
        exists = await session.execute(
            select(CharityProject).where(
                CharityProject.name == payload["name"]
            )
        )
        found = exists.scalars().first()
        if found is not None and found.id != project.id:
            raise HTTPException(
                status_code=400,
                detail="Проект с таким именем уже существует!",
            )

    # Нельзя ставить full_amount меньше уже вложенной суммы
    if (
        "full_amount" in payload
        and payload["full_amount"] is not None
    ):
        if payload["full_amount"] < project.invested_amount:
            raise HTTPException(
                status_code=400,
                detail=(
                    "Нелья установить значение full_amount меньше уже "
                    "вложенной суммы."
                ),
            )

    for field, value in payload.items():
        setattr(project, field, value)

    if (
        project.invested_amount >= project.full_amount
        and not project.fully_invested
    ):
        project.fully_invested = True
        project.close_date = datetime.utcnow()

    await session.commit()
    return project


@router.delete(
    "/{project_id}",
    response_model=CharityProjectDB,
    description=(
        "Удалить целевой проект.\n\n"
        "Нельзя удалить проект, в который уже были инвестированы средства."
    ),
)
async def delete_charity_project(
    project_id: int,
    session: AsyncSession = Depends(get_async_session),
    _=Depends(current_superuser),
):
    project = await get_project_or_404(project_id, session)

    # Нельзя удалить проект, если в него уже инвестировали (или он закрыт)
    if (
        project.invested_amount > 0
        or project.fully_invested
    ):
        raise HTTPException(
            status_code=400,
            detail="В проект были внесены средства, не подлежит удалению!",
        )

    await session.delete(project)
    await session.commit()
    return project