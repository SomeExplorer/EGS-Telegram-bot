import asyncio

from src.logger import logger
from src.bot.telegram_bot import TelegramBot


async def main() -> None:
    telegram_bot = TelegramBot()
    logger.info("Запуск Telegram бота")
    await telegram_bot.start_polling()


if __name__ == "__main__":
    asyncio.run(main())
