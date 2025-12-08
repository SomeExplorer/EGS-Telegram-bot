import asyncio

from src.bots.telegram_bot import TelegramBot
from src.notifications.notificator import Notificator


async def main() -> None:
    notificator = Notificator(TelegramBot())
    print("Notificator is running...")
    await notificator.run()


if __name__ == "__main__":
    asyncio.run(main())
