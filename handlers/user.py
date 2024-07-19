from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
import re
import logging
from utils.bitrix import add_user_to_bitrix
import json

class UserStates(StatesGroup):
    waiting_for_first_name = State()
    waiting_for_last_name = State()
    waiting_for_contact = State()

def register_user_handlers(dp: Dispatcher):
    dp.register_callback_query_handler(handle_inline_buttons, lambda c: c.data == "Создать пользователя")
    dp.register_message_handler(process_first_name, state=UserStates.waiting_for_first_name)
    dp.register_message_handler(process_last_name, state=UserStates.waiting_for_last_name)
    dp.register_message_handler(process_contact, state=UserStates.waiting_for_contact)

async def handle_inline_buttons(callback_query: types.CallbackQuery, state: FSMContext):
    logging.debug(f"Обработка инлайн-кнопки: {callback_query.data}")
    await UserStates.waiting_for_first_name.set()
    await callback_query.message.answer("Вы выбрали: Создать пользователя. Введите имя пользователя:")
    await callback_query.answer()

async def process_first_name(message: types.Message, state: FSMContext):
    await state.update_data(first_name=message.text.strip())
    await UserStates.waiting_for_last_name.set()
    await message.answer("Введите фамилию пользователя:")

async def process_last_name(message: types.Message, state: FSMContext):
    await state.update_data(last_name=message.text.strip())
    await UserStates.waiting_for_contact.set()
    await message.answer("Введите email или телефон пользователя:")

def is_valid_email(email: str) -> bool:
    email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return re.match(email_regex, email) is not None

async def process_contact(message: types.Message, state: FSMContext):
    contact = message.text.strip()

    if not is_valid_email(contact):
        await message.answer("Неверный формат email. Пожалуйста, введите правильный email.")
        return

    data = await state.get_data()
    user_info = {
        'first_name': data.get('first_name'),
        'last_name': data.get('last_name'),
        'email': contact
    }

    logging.debug(f"Данные для Bitrix: {user_info}")

    bitrix_data = {
        'NAME': user_info['first_name'],
        'LAST_NAME': user_info['last_name'],
        'EMAIL': user_info['email'],
        'EXTRANET': 'Y',
        'SONET_GROUP_ID': [0]
    }

    bitrix_data_json = json.dumps(bitrix_data, ensure_ascii=False, indent=4)
    logging.debug(f"Данные для Bitrix в формате JSON: {bitrix_data_json}")

    success = await add_user_to_bitrix(bitrix_data)
    if success:
        await message.answer("Пользователь успешно создан в Bitrix.")
    else:
        await message.answer("Ошибка при создании пользователя в Bitrix.")
    
    await state.finish()
