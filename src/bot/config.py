from pathlib import Path

from pydantic import BaseModel


class BotSettings(BaseModel):
    db_name: str = "bot_db.sqlite"

    @property
    def db_path(self) -> str:
        data_dir = Path(__file__).resolve().parents[2] / "data"
        data_dir.mkdir(parents=True, exist_ok=True)
        db_path = data_dir / self.db_name

        return db_path.as_posix()

bot_settings = BotSettings()
