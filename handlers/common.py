from aiogram import Dispatcher, types


def register_common_handlers(dp: Dispatcher):
    @dp.message_handler(commands=['start'])
    async def send_welcome(message: types.Message):
        username = message.from_user.username
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        buttons = ["Загрузить фото"]
        buttons.append("Создать пользователя в Bitrix")
        buttons.append("Поздравить пользователя")
        keyboard.add(*buttons)
        await message.answer(f"Привет, {username}!", reply_markup=keyboard)
