from requests import Session, RequestException, HTTPError
from pydantic import ValidationError

from src.logger import logger
from src.schemas.store_schema import StoreSchema
from src.schemas.game_info_schema import GameInfoSchema
from src.notifications.constants import BASE_API_URL


def _get_store_data(locale: str, country: str, allow_countries: str) -> StoreSchema:
    api_uri = f"{BASE_API_URL}/freeGamesPromotions?locale={locale}&country={country}&allowCountries={allow_countries}"

    try:
        with Session() as session:
            response = session.get(api_uri)

        if response.status_code != 200:
            response.raise_for_status()
            raise HTTPError(f"Unexpected status code {response.status_code}")

        try:
            validated_store_data = StoreSchema.model_validate(response.json())
        except ValidationError as e:
            logger.exception("Store schema is not correct: %s", str(e))
            raise e
        else:
            return validated_store_data

    except RequestException as e:
        logger.exception("API request error: %s", str(e))
        raise e


def get_free_games(locale: str, country: str, allow_countries: str) -> list[GameInfoSchema]:
    store_data = _get_store_data(locale, country, allow_countries)
    free_games = store_data.data.catalog.search_store.elements
    return free_games
