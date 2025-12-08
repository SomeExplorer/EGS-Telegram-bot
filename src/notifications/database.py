from datetime import datetime, timedelta

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.notifications.models import Base, SentNotificationsModel


sync_engine = create_engine(url="sqlite:///notifications.sqlite", echo=True)
sync_session = sessionmaker(sync_engine)
Base.metadata.create_all(sync_engine)


class Database:
    @classmethod
    def insert_notification(cls, game_id: str, completed_at: datetime) -> None:
        with sync_session() as session:
            notification = SentNotificationsModel(game_id=game_id, completed_at=completed_at)
            session.add(notification)
            session.commit()

    @classmethod
    def select_last_30_days_games_ids(cls) -> list[str]:
        with sync_session() as session:
            games_ids = (
                session.query(SentNotificationsModel.game_id)
                .filter(SentNotificationsModel.completed_at >= datetime.now() - timedelta(days=30))
                .all()
            )
            return [obj[0] for obj in games_ids]
