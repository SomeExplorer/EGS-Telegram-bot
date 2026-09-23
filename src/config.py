from pydantic import BaseModel


class GlobalSettings(BaseModel):
    locale: str = "ru"
    country: str = "RU"
    allow_countries: str = "RU"

global_settings = GlobalSettings()
