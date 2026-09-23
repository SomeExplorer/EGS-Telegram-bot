from pathlib import Path

from pydantic import BaseModel


class NotifierSettings(BaseModel):
    db_name: str = "notifier_db.sqlite"

    @property
    def db_path(self) -> str:
        data_dir = Path(__file__).resolve().parents[2] / "data"
        data_dir.mkdir(parents=True, exist_ok=True)
        db_path = data_dir / self.db_name

        return db_path.as_posix()

notifier_settings = NotifierSettings()
