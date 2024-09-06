import logging

from aiogram import Bot, Dispatcher, executor
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.types import BotCommand
from aiogram.contrib.fsm_storage.memory import MemoryStorage


from config import API_TOKEN
from handlers.common import register_handlers_common
from handlers.photo import register_photo_handlers
from handlers.congratulation import register_congratulation_handlers
from handlers.booking import booking_user_handlers
from handlers.user import register_user_handlers
from handlers.del_booking import register_del_booking_handlers

logging.basicConfig(level=logging.DEBUG)
bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
dp.middleware.setup(LoggingMiddleware())


register_handlers_common(dp)
register_photo_handlers(dp)
register_congratulation_handlers(dp)
booking_user_handlers(dp)
register_user_handlers(dp)
register_del_booking_handlers(dp)

async def on_startup(dp):
    await bot.set_my_commands([
        BotCommand(command="/start", description="Начать работу с ботом"),
    ])

if __name__ == "__main__":
    executor.start_polling(dp, on_startup=on_startup, allowed_updates=["message", "callback_query"])
