import asyncio

from src.bot.telegram_bot import TelegramBot


async def main() -> None:
    telegram_bot = TelegramBot()
    print("Telegram bot is running...")
    await telegram_bot.start_polling()


if __name__ == "__main__":
    asyncio.run(main())
