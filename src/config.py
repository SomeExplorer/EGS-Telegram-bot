from pydantic import BaseModel
from pydantic_extra_types.timezone_name import TimeZoneName


class GlobalSettings(BaseModel):
    locale: str = "ru"
    country: str = "RU"
    allow_countries: str = "RU"
    timezone: TimeZoneName = "Europe/Moscow"

global_settings = GlobalSettings()
