from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.charity_project import CharityProject
from app.models.donation import Donation


def _close_object(obj) -> None:
    obj.fully_invested = True
    obj.close_date = datetime.utcnow()


async def invest_into_project(
    project: CharityProject,
    session: AsyncSession,
) -> CharityProject:
    project.invested_amount = project.invested_amount or 0

    donations_result = await session.execute(
        select(Donation)
        .where(Donation.fully_invested.is_(False))
        .order_by(Donation.create_date)
    )
    donations = donations_result.scalars().all()

    for donation in donations:
        donation.invested_amount = donation.invested_amount or 0

        if project.fully_invested:
            break

        project_need = project.full_amount - project.invested_amount
        donation_free = donation.full_amount - donation.invested_amount
        to_invest = min(project_need, donation_free)

        if to_invest <= 0:
            continue

        project.invested_amount += to_invest
        donation.invested_amount += to_invest

        if donation.invested_amount == donation.full_amount:
            _close_object(donation)

        if project.invested_amount == project.full_amount:
            _close_object(project)

    return project


async def invest_donation(
    donation: Donation,
    session: AsyncSession,
) -> Donation:
    """Вкладывает одно пожертвование в самые старые открытые проекты."""
    donation.invested_amount = donation.invested_amount or 0

    projects_result = await session.execute(
        select(CharityProject)
        .where(CharityProject.fully_invested.is_(False))
        .order_by(CharityProject.create_date)
    )
    projects = projects_result.scalars().all()

    for project in projects:
        project.invested_amount = project.invested_amount or 0

        if donation.fully_invested:
            break

        project_need = project.full_amount - project.invested_amount
        donation_free = donation.full_amount - donation.invested_amount
        to_invest = min(project_need, donation_free)

        if to_invest <= 0:
            continue

        project.invested_amount += to_invest
        donation.invested_amount += to_invest

        if project.invested_amount == project.full_amount:
            _close_object(project)

        if donation.invested_amount == donation.full_amount:
            _close_object(donation)

    return donation