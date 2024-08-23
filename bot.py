# вывод ошибок
import logging

# библиотеки и модули 
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.types import BotCommand
from aiogram.dispatcher.middlewares import BaseMiddleware
from aiogram.dispatcher.handler import CancelHandler
from aiogram.contrib.fsm_storage.memory import MemoryStorage

# вызов функции и апи токенов
from config import API_TOKEN, ALLOWED_USERS
from handlers.common import register_handlers_common
from handlers.photo import register_photo_handlers
from handlers.user import register_user_handlers
from handlers.congratulation import register_congratulation_handlers
from handlers.help import register_help_command
from handlers.booking import booking_user_handlers

# храненение данных
logging.basicConfig(level=logging.DEBUG)
bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
dp.middleware.setup(LoggingMiddleware())

# класс отвечающий за доступ к боту
class AccessMiddleware(BaseMiddleware):
    async def on_process_message(self, message: types.Message, data: dict):
        username = f"@{message.from_user.username}" if message.from_user.username else None
        logging.debug(f"Username: {username}")
        if not username or username not in ALLOWED_USERS:
            await message.answer("У вас нет доступа к этому боту.")
            raise CancelHandler()

# вызов функции 
dp.middleware.setup(AccessMiddleware())

register_handlers_common(dp)
register_photo_handlers(dp)
register_user_handlers(dp)
register_congratulation_handlers(dp)
register_help_command(dp)
booking_user_handlers(dp)

# команды 
async def on_startup(dp):
    await bot.set_my_commands([
        BotCommand(command="/start", description="Начать работу с ботом"),
        BotCommand(command="/help", description="Справка")
    ])
    logging.info("Бот запущен и готов к работе")

if __name__ == "__main__":
    executor.start_polling(dp, on_startup=on_startup, allowed_updates=["message", "callback_query"])
