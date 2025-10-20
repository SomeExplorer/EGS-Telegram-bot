import requests
from pydantic import ValidationError

from src.schemas.store_schema import StoreSchema
from src.schemas.game_info_schema import GameInfoSchema


def get_store_data(
    locale: str = "ru", country: str = "RU", allow_countries: str = "RU"
) -> dict | None:
    api_uri = (
        "https://store-site-backend-static.ak.epicgames.com/"
        f"freeGamesPromotions?locale={locale}&country={country}&allowCountries={allow_countries}"
    )
    with requests.Session() as session:
        try:
            response = session.get(api_uri)
            response.raise_for_status()
            data = response.json()
            return data
        except requests.exceptions.ConnectionError as e:
            print(f"Connection error: {e}")
        except requests.exceptions.Timeout as e:
            print(f"Request timed out: {e}")
        except requests.exceptions.RequestException as e:
            print(f"An unexpected request error: {e}")


def get_free_games(
    locale: str = "ru", country: str = "RU", allow_countries: str = "RU"
) -> list[GameInfoSchema] | None:
    try:
        store_data = get_store_data(locale, country, allow_countries)
        if not store_data:
            return
        store = StoreSchema(**get_store_data())
    except ValidationError as e:
        print(f"Validation error: {e}")
    else:
        free_games = store.data.catalog.search_store.elements

        return free_games
