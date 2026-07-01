import datetime
from sqlalchemy import String , Boolean
from sqlalchemy.orm import Mapped , mapped_column , relationship
from app.core.database import Base

from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from app.models.experiment import Experiment


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key = True, autoincrement=True)
    username : Mapped[str] = mapped_column(String(50), unique = True , index=True)
    email : Mapped[str] = mapped_column(String(255), unique = True ,index = True)
    hashed_password : Mapped[str] = mapped_column(String(255))
    is_active : Mapped[bool] = mapped_column(Boolean , default=True)
    created_at : Mapped[datetime.datetime] = mapped_column(default = datetime.datetime.utcnow)
    updated_at : Mapped[datetime.datetime | None ] = mapped_column(nullable = True)
    experiments: Mapped[list["Experiment"]] = relationship(back_populates="owner")