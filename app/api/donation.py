from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_async_session
from app.core.user import current_superuser, current_user
from app.models.donation import Donation
from app.models.user import User
from app.schemas.donation import DonationCreate, DonationDB, DonationFullInfoDB
from app.services.investing import invest_donation

router = APIRouter(prefix="/donation", tags=["donations"])


@router.post(
    "/",
    response_model=DonationDB,
    description="Создать пожертвование.",
)
async def create_donation(
    donation_in: DonationCreate,
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_user),
):
    donation = Donation(**donation_in.model_dump(), user_id=user.id)
    session.add(donation)
    await session.flush()

    await invest_donation(donation, session)

    await session.commit()
    return donation


@router.get("/my", response_model=list[DonationDB])
async def get_my_donations(
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_user),
):
    result = await session.execute(
        select(Donation)
        .where(Donation.user_id == user.id)
        .order_by(Donation.create_date)
    )
    return result.scalars().all()


@router.get(
    "/",
    response_model=list[DonationFullInfoDB],
    description="Показать список всех пожертвований.",
)
async def get_all_donations(
    session: AsyncSession = Depends(get_async_session),
    _=Depends(current_superuser),
):
    result = await session.execute(
        select(Donation).order_by(Donation.create_date)
    )
    return result.scalars().all()