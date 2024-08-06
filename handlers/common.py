# проверка ошибки
import logging

# библотеки 
from aiogram import types
from aiogram.dispatcher import Dispatcher

# функция отвечающая за кнопку старт
def register_handlers_common(dp: Dispatcher):
    dp.register_message_handler(start_command, commands=['start'])

# последующие кнопки
async def start_command(message: types.Message):
    logging.debug("Обработка команды /start")
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text="Создать пользователя", callback_data="Создать пользователя"))
    keyboard.add(types.InlineKeyboardButton(text="Поздравить пользователя", callback_data="Поздравить пользователя"))
    keyboard.add(types.InlineKeyboardButton(text="Загрузить фото", callback_data="Загрузить фото"))
    keyboard.add(types.InlineKeyboardButton(text="Забронировать место", callback_data="Забронировать место"))
    keyboard.add(types.InlineKeyboardButton(text="Отменить переговорную комнату", callback_data="Отменить переговорную комнату"))
    await message.answer("Выберите действие:", reply_markup=keyboard)
