from pydantic import BaseModel, Field


class GameInfoMessage(BaseModel, frozen=True):
    title: str = Field(pattern=r"^🎮 .*\{game_title\}$")
    promotion_date: str = Field(pattern=r"📅 .*\{promotion_end_date\}$")
    description: str = Field(pattern=r"^.*\{game_description\}.*$")
    url: str = Field(pattern=r"^.*\{game_url\}$")

class WelcomeMessage(BaseModel, frozen=True):
    content: str = Field(pattern=r"^.*\{username\}.*$")

class MessageTemplate(BaseModel, frozen=True):
    welcome_message: WelcomeMessage
    game_info_message: GameInfoMessage


LOCALES: dict[str, MessageTemplate] = {
    "ru": MessageTemplate(
        welcome_message=WelcomeMessage(
            content="Привет, {username}! Этот бот будет уведомлять тебя о бесплатных раздачах игр в Epic Games Store.",
        ),
        game_info_message=GameInfoMessage(
            title="🎮 {game_title}",
            promotion_date="📅 Доступно до {promotion_end_date}",
            description="{game_description}",
            url="{game_url}",
        ),
    ),
    "en": MessageTemplate(
        welcome_message=WelcomeMessage(
            content="Hi, {username}! This bot will notify you about free game giveaways on the Epic Games Store.",
        ),
        game_info_message=GameInfoMessage(
            title="🎮 {game_title}",
            promotion_date="📅 Available until {promotion_end_date}",
            description="{game_description}",
            url="{game_url}",
        ),
    ),
}
