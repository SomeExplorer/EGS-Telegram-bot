from pydantic import BaseModel, Field


class UsersSchema(BaseModel):
    user_id: int = Field(alias="id")
    username: str
    first_name: str
    last_name: str | None
    language_code: str | None
