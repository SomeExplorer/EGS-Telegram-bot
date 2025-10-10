from pydantic import BaseModel, Field

from src.schemas.game_info_schema import GameInfoSchema


class SearchStoreSchema(BaseModel):
    elements: list[GameInfoSchema]


class CatalogSchema(BaseModel):
    search_store: SearchStoreSchema = Field(alias="searchStore")


class DataSchema(BaseModel):
    catalog: CatalogSchema = Field(alias="Catalog")


class StoreSchema(BaseModel):
    data: DataSchema
