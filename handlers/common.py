import logging
from aiogram import types
from aiogram.dispatcher import Dispatcher

def register_handlers_common(dp: Dispatcher):
    dp.register_message_handler(start_command, commands=['start'])

async def start_command(message: types.Message):
    logging.debug("Обработка команды /start")
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text="Создать пользователя", callback_data="Создать пользователя"))
    keyboard.add(types.InlineKeyboardButton(text="Поздравить пользователя", callback_data="Поздравить пользователя"))
    keyboard.add(types.InlineKeyboardButton(text="Загрузить фото", callback_data="Загрузить фото"))
    await message.answer("Выберите действие:", reply_markup=keyboard)
