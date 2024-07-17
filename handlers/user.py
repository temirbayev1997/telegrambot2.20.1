from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
import logging
from utils.bitrix import add_user_to_bitrix, check_email_exists_in_bitrix

class UserStates(StatesGroup):
    creating_user = State()

def register_user_handlers(dp: Dispatcher):
    dp.register_callback_query_handler(handle_inline_buttons, lambda c: c.data == "Создать пользователя")
    dp.register_message_handler(process_creating_user, state=UserStates.creating_user)

async def handle_inline_buttons(callback_query: types.CallbackQuery, state: FSMContext):
    logging.debug(f"Обработка инлайн-кнопки: {callback_query.data}")
    await UserStates.creating_user.set()
    await callback_query.message.answer("Вы выбрали: Создать пользователя. Введите данные пользователя в формате: Имя, Фамилия, Email/Телефон")
    await callback_query.answer()

async def process_creating_user(message: types.Message, state: FSMContext):
    user_data = message.text.split(',')
    if len(user_data) != 3:
        await message.answer("Неверный формат. Пожалуйста, введите данные пользователя в формате: Имя, Фамилия, Email/Телефон")
        return

    user_info = {
        'first_name': user_data[0].strip(),
        'last_name': user_data[1].strip(),
        'contact': user_data[2].strip()
    }

    contact_type = 'email' if '@' in user_info['contact'] else 'phone'

    if contact_type == 'email' and await check_email_exists_in_bitrix(user_info['contact']):
        await message.answer("Пользователь с таким email уже существует в Bitrix.")
        await state.finish()
        return

    success = await add_user_to_bitrix(user_info, contact_type)
    if success:
        await message.answer("Пользователь успешно создан в Bitrix.")
    else:
        await message.answer("Ошибка при создании пользователя в Bitrix.")
    
    await state.finish()
