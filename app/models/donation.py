from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base


class Donation(Base):
    __tablename__ = "donation"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    comment: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
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

    user_id: Mapped[int] = mapped_column(
        ForeignKey("user.id"),
        nullable=False,
    )
    user = relationship("User", lazy="selectin")