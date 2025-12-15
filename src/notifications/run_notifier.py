import asyncio

from src.logger import logger
from src.bot.telegram_bot import TelegramBot
from src.notifications.notifier import Notifier


async def main() -> None:
    notifier = Notifier(TelegramBot())
    logger.info(f"Запуск {notifier.__class__.__name__}")
    await notifier.run()


if __name__ == "__main__":
    asyncio.run(main())
