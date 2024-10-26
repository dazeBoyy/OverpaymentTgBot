import os
import asyncio
from aiogram import Bot, Dispatcher
from app.handlers import router
from dotenv import load_dotenv
from app.database.models import async_main



async def main():
    await async_main()
    load_dotenv()
    bot = Bot(token=os.getenv('TOKEN'))
    dp = Dispatcher()

    dp.include_router(router)
    await dp.start_polling(bot)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Бот выключен')
