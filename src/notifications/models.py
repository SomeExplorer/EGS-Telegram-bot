from datetime import datetime

from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase


class Base(DeclarativeBase):
    pass


class SentNotificationsModel(Base):
    __tablename__ = "sent_notifications"

    id: Mapped[int] = mapped_column(primary_key=True)
    game_id: Mapped[str]
    completed_at: Mapped[datetime]
