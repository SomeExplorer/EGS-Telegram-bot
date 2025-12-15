from datetime import datetime

from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase


class Base(DeclarativeBase):
    repr_cols = tuple()

    def __repr__(self):
        cols = []
        for idx, col in enumerate(self.__table__.columns.keys()):
            if col in self.repr_cols:
                cols.append(f"{col}={getattr(self, col)}")

        return f"<{self.__class__.__name__} {', '.join(cols)}>"


class SentNotificationsModel(Base):
    __tablename__ = "sent_notifications"
    repr_cols = ("id", "game_id", )

    id: Mapped[int] = mapped_column(primary_key=True)
    game_id: Mapped[str]
    completed_at: Mapped[datetime]
