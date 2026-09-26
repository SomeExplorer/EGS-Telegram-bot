import asyncio
from datetime import datetime
from collections import namedtuple
from os import getenv
from zoneinfo import ZoneInfo

from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.utils.formatting import as_section, Bold, Url, as_list
from aiogram.exceptions import TelegramRetryAfter, TelegramServerError, TelegramNotFound
from dotenv import load_dotenv
from tenacity import retry
from tenacity.stop import stop_after_attempt
from tenacity.wait import wait_fixed
from tenacity.retry import retry_if_exception_type

from src.schemas.users_schema import UsersSchema
from src.schemas.game_info_schema import GameInfoSchema
from src.bot.database import Database
from src.bot.base_bot import BaseBot
from src.bot.message_templates import LOCALES
from src.bot.constants import GAME_BASE_URL
from src.config import global_settings
from src.logger import logger

load_dotenv()
MESSAGES = LOCALES[global_settings.locale.lower()] if LOCALES.get(global_settings.locale) else LOCALES["en"]
TOKEN = getenv("BOT_TOKEN")
dp = Dispatcher()
MessageContent = namedtuple("MessageContent", ["text", "img_url"])


class TelegramBot(BaseBot):
    __bot = Bot(token=TOKEN)

    async def start_polling(self) -> None:
        await dp.start_polling(self.__bot)

    @staticmethod
    @dp.message(Command("start"))
    async def __send_welcome_message(message: Message) -> None:
        user = message.from_user
        Database.insert_user(UsersSchema.model_validate(user.__dict__))
        msg_text = MESSAGES.welcome_message.content.format(username=user.first_name)
        await message.answer(msg_text)

    async def notify_users(self, game: GameInfoSchema) -> None:
        semaphore = asyncio.Semaphore(20)
        successes = 0

        @retry(
            stop=stop_after_attempt(7),
            wait=wait_fixed(5),
            retry=retry_if_exception_type((TelegramRetryAfter, TelegramServerError)),
        )
        async def send_message(user_id: int, content: MessageContent) -> None:
            nonlocal successes
            async with semaphore:
                try:
                    await self.__bot.send_photo(
                        **content.text.as_caption_kwargs(), chat_id=user_id, photo=content.img_url
                    )
                    successes += 1
                except TelegramNotFound as e:
                    logger.error("TelegramNotFound", exc_info=True)
                    if "user not found" in str(e).lower():
                        Database.delete_user_by_id(user_id)

        message_content = self._get_game_info_message_content(game)
        user_ids = Database.select_user_ids()
        tasks = [send_message(user_id, message_content) for user_id in user_ids]
        await asyncio.gather(*tasks)
        logger.info(f"Telegram бот успешно оповестил {successes} пользователей об игре {game.title} (id={game.id})")

    @staticmethod
    def _get_game_info_message_content(game: GameInfoSchema) -> MessageContent:
        img_url = game.wide_img_url
        title = Bold(MESSAGES.game_info_message.title.format(game_title=game.title))
        promotion_date = MESSAGES.game_info_message.promotion_date.format(
            promotion_end_date=datetime.strftime(
                game.free_offer.end_date.astimezone(tz=ZoneInfo(global_settings.timezone)),
                format="%d.%m.%Y %H:%M"
            )
        )
        description = MESSAGES.game_info_message.description.format(game_description=game.description)
        url = Url(
            MESSAGES.game_info_message.url.format(game_url=f"{GAME_BASE_URL}{game.catalog_ns.mappings[0].page_slug}")
        )
        body = as_list(promotion_date, description, url, sep="\n\n")
        message_text = as_section(title, body)

        return MessageContent(message_text, img_url)
