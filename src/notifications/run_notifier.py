import asyncio
import logging
from src.logging_config import configure_logging
from src.bot.telegram_bot import TelegramBot
from src.notifications.notifier import Notifier


async def main() -> None:
    notifier = Notifier(TelegramBot())
    configure_logging()
    logger = logging.getLogger("notifier")

    logger.info(f"Starting notifier...")
    await notifier.run()


if __name__ == "__main__":
    asyncio.run(main())
