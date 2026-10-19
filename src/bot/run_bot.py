import asyncio
import logging

from src.bot.telegram_bot import TelegramBot
from src.logging_config import configure_logging


async def main() -> None:
    telegram_bot = TelegramBot()
    configure_logging()
    logger = logging.getLogger("telegram_bot")

    logger.info("Starting Telegram bot...")
    await telegram_bot.start_polling()


if __name__ == "__main__":
    asyncio.run(main())
