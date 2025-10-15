import os
import sys
import asyncio
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher

from app.database.models import db
from app.handlers import handlers
from app.admin import admin
from app.materials import material
from app.edit_data import edit_data

load_dotenv()


async def startup(dispatcher: Dispatcher, bot: Bot):
    await db.connect()
    await db.init_db()
    print("Бот запущен...!")


async def shutdown(dispatcher: Dispatcher, bot: Bot):
    await db.close()
    print("Бот остановлен...!")


async def main():
    bot = Bot(token=os.getenv('TG_TOKEN'))
    dp = Dispatcher()

    dp.startup.register(startup)
    dp.shutdown.register(shutdown)
    dp.include_routers(handlers, admin, material, edit_data)

    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        if sys.platform.startswith("win"):
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        asyncio.run(main())
    except KeyboardInterrupt:
        pass

