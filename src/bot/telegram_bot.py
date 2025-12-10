import asyncio
from datetime import datetime
from collections import namedtuple
from os import getenv

from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.utils.formatting import as_section, Text, Bold, Url, as_list, Underline
from aiogram.exceptions import TelegramRetryAfter, TelegramServerError
from dotenv import load_dotenv
from tenacity import retry
from tenacity.stop import stop_after_attempt
from tenacity.wait import wait_fixed
from tenacity.retry import retry_if_exception_type

from src.schemas.users_schema import UsersSchema
from src.schemas.game_info_schema import GameInfoSchema, ImageType
from src.bot.database import Database
from src.bot.base_bot import BaseBot

load_dotenv()
TOKEN = getenv("BOT_TOKEN")
dp = Dispatcher()

MessageContent = namedtuple("MessageContent", ["text", "img_url"])


class TelegramBot(BaseBot):
    __bot = Bot(token=TOKEN)

    async def start_polling(self) -> None:
        await dp.start_polling(self.__bot)

    @staticmethod
    @dp.message(Command("start"))
    async def handle_command_start(message: Message) -> None:
        user = message.from_user
        Database.insert_user(UsersSchema.model_validate(user.__dict__))
        msg_text = (
            f"Привет, {user.first_name}! "
            f"Этот бот будет уведомлять тебя о бесплатных раздачах игр в Epic Games Store."
        )
        await message.answer(msg_text)

    async def notify_users(self, game: GameInfoSchema) -> None:
        semaphore = asyncio.Semaphore(20)

        @retry(
            stop=stop_after_attempt(7),
            wait=wait_fixed(5),
            retry=retry_if_exception_type((TelegramRetryAfter, TelegramServerError)),
        )
        async def send_message(user_id: int, content: MessageContent) -> None:
            async with semaphore:
                await self.__bot.send_photo(**content.text.as_caption_kwargs(), chat_id=user_id, photo=content.img_url)

        message_content = self.get_message_content(game)
        user_ids = Database.select_user_ids()
        tasks = [send_message(user_id, message_content) for user_id in user_ids]
        await asyncio.gather(*tasks)

    @staticmethod
    def get_message_content(game: GameInfoSchema) -> MessageContent:
        img_url = str(next(filter(lambda x: x.type == ImageType.OFFER_IMAGE_WIDE, game.key_images)).url)
        title = Text("🎮 ", Bold(game.title))

        if game.promotions.promotional_offers:
            end_date = game.promotions.promotional_offers[0].promotional_offers[0].end_date
        else:
            end_date = game.promotions.upcoming_promotional_offers[0].promotional_offers[0].end_date

        date_info = Text("Доступно до ", Underline(datetime.strftime(end_date, "%d.%m.%Y %H:%M")))
        description = f"\n{game.description}\n"
        game_url = Url(f"https://store.epicgames.com/ru/p/{game.catalog_ns.mappings[0].page_slug}")

        body = as_list(date_info, description, game_url)
        text = as_section(title, body)

        return MessageContent(text, img_url)
