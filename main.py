import asyncio

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from config import BOT_TOKEN
from database.connection import connect_db, close_db
from utils.logger import logger


dp = Dispatcher()


async def on_startup(bot: Bot):

    logger.info("=" * 50)
    logger.info("NC ENGINE HOST STARTING...")
    logger.info("=" * 50)

    await connect_db()

    me = await bot.get_me()

    logger.info(f"Bot Name : {me.full_name}")
    logger.info(f"Username : @{me.username}")
    logger.info(f"Bot ID   : {me.id}")

    logger.info("Database Connected")
    logger.info("Bot Started Successfully")


async def on_shutdown(bot: Bot):

    logger.info("Stopping Bot...")

    await close_db()

    session = await bot.get_session()
    await session.close()

    logger.info("Shutdown Complete")


async def main():

    if not BOT_TOKEN:
        raise RuntimeError("BOT_TOKEN not found in .env")

    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(
            parse_mode=ParseMode.HTML
        )
    )

    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    logger.info("Polling Started...")

    await dp.start_polling(bot)


if __name__ == "__main__":

    try:
        asyncio.run(main())

    except (KeyboardInterrupt, SystemExit):

        logger.info("Bot Stopped.")
