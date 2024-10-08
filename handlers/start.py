from aiogram import types
from config import CREATE_USERS

async def start_command(message: types.Message):
    user_username = message.from_user.username
    
    if not user_username:
        user_username = message.from_user.first_name or message.from_user.last_name or "Пользователь"
    else:
        user_username = f"@{user_username}"  

    keyboard = types.InlineKeyboardMarkup()
    if user_username in CREATE_USERS:
        keyboard.add(types.InlineKeyboardButton(text="Создать пользователя", callback_data="Создать пользователя"))

    keyboard.add(types.InlineKeyboardButton(text="Поздравить пользователя", callback_data="Поздравить пользователя"))
    keyboard.add(types.InlineKeyboardButton(text="Загрузить фото", callback_data="Загрузить фото"))
    keyboard.add(types.InlineKeyboardButton(text="Забронировать место", callback_data="Забронировать место"))
    keyboard.add(types.InlineKeyboardButton(text="Отменить бронирвание", callback_data="Отменить бронирвание"))
    await message.answer(f"Привет, @{user_username} меню:", reply_markup=keyboard)
