from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import BotCommand
from aiogram.utils import executor
from config import API_TOKEN
from handlers import register_handlers
import logging

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

async def set_commands(bot: Bot):
    commands = [
        BotCommand(command="/start", description="Начать работу с ботом"),
        BotCommand(command="/create_user", description="Создать нового пользователя в Bitrix"),
    ]
    await bot.set_my_commands(commands)

async def on_startup(dp):
    await set_commands(dp.bot)

register_handlers(dp)

if __name__ == "__main__":
    executor.start_polling(dp, on_startup=on_startup)
