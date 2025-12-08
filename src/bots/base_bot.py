from abc import abstractmethod, ABC

from src.schemas.game_info_schema import GameInfoSchema


class BaseBot(ABC):
    @abstractmethod
    async def notify_users(self, game: GameInfoSchema) -> None: ...
