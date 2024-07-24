from aiogram import types
from aiogram.dispatcher import Dispatcher

def register_help_command(dp: Dispatcher):
    dp.register_message_handler(help_command, commands=["help"])
    dp.register_callback_query_handler(handlers_inline_buttons, lambda c: c.data and c.data.startswith('option_'))

async def help_command(message: types.Message):
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text="Option 1", callback_data="option_1"))
    keyboard.add(types.InlineKeyboardButton(text="Option 2", callback_data="option_2"))
    keyboard.add(types.InlineKeyboardButton(text="Option 3", callback_data="option_3"))
    keyboard.add(types.InlineKeyboardButton(text="Option 4", callback_data="option_4"))
    
    await message.answer("Выберите действие:", reply_markup=keyboard)

async def handlers_inline_buttons(callback_query: types.CallbackQuery):
    await callback_query.answer(f"You selected {callback_query.data}")
    await callback_query.message.edit_text(f"You selected {callback_query.data}")
