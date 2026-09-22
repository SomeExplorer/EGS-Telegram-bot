from pydantic import BaseModel

class Settings(BaseModel):
    locale: str = "ru"
    country: str = "RU"
    allow_countries: str = "RU"

settings = Settings()
