from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, PositiveInt


class DonationCreate(BaseModel):
    full_amount: PositiveInt
    comment: Optional[str] = None

    model_config = ConfigDict(extra="forbid")


class DonationDB(BaseModel):
    id: int
    full_amount: PositiveInt
    comment: Optional[str] = None
    create_date: datetime

    model_config = ConfigDict(from_attributes=True, extra="forbid")


class DonationFullInfoDB(BaseModel):
    id: int
    full_amount: PositiveInt
    comment: Optional[str] = None
    create_date: datetime
    user_id: int              # <-- добавь это
    invested_amount: int
    fully_invested: bool
    close_date: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True, extra="forbid")