# проверка ошибки
import logging

# библотеки 
from aiogram import types
from aiogram.dispatcher import Dispatcher
from aiogram.dispatcher.middlewares import BaseMiddleware
from aiogram.dispatcher.handler import CancelHandler
from aiogram import Bot, Dispatcher,types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from config import ALLOWED_USERS, API_TOKEN

bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

class AccessMiddleware(BaseMiddleware):
    async def on_process_message(self, message: types.Message, data: dict):
        username = f"@{message.from_user.username}" if message.from_user.username else None
        logging.debug(f"Username: {username}")
        if not username or username not in ALLOWED_USERS:
            await message.answer("У вас нет доступа к этому боту.")
            raise CancelHandler()
        
# функция отвечающая за кнопку старт
from aiogram import Dispatcher
from handlers.start import start_command

def register_handlers_common(dp: Dispatcher):
    dp.register_message_handler(start_command, commands=['start'])

