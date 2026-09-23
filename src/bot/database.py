from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

from src.schemas.users_schema import UsersSchema
from src.bot.models import Base, UsersModel
from src.bot.config import bot_settings
from src.logger import logger


sync_engine = create_engine(url=f"sqlite:///{bot_settings.db_path}", echo=False, pool_size=1, max_overflow=2)
sync_session = sessionmaker(sync_engine)
Base.metadata.create_all(sync_engine)


class Database:
    @classmethod
    def insert_user(cls, user: UsersSchema) -> None:
        with sync_session() as session:
            db_user = UsersModel(**user.model_dump())
            if not session.query(UsersModel).filter_by(user_id=db_user.user_id).first():
                session.add(db_user)
                session.commit()
                logger.info(f"INSERT {db_user} INTO {UsersModel.__tablename__}")

    @classmethod
    def delete_user_by_id(cls, user_id: int) -> None:
        with sync_session() as session:
            user_to_delete = session.get(UsersModel, user_id)
            if user_to_delete:
                session.delete(user_to_delete)
                session.commit()
                logger.info(f"DELETE {user_to_delete} FROM {UsersModel.__tablename__}")

    @classmethod
    def select_user_ids(cls) -> list[int]:
        with sync_session() as session:
            user_ids = session.scalars(select(UsersModel.user_id)).all()
            return user_ids
