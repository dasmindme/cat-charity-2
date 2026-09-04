from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


class CharityProject(Base):
    __tablename__ = "charityproject"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
    )
    description: Mapped[str] = mapped_column(Text, nullable=False)
    full_amount: Mapped[int] = mapped_column(Integer, nullable=False)

    invested_amount: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )
    fully_invested: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    create_date: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )
    close_date: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        nullable=True,
    )