from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from utils.bitrix import create_user_in_bitrix
import re
import logging

class UserCreationForm(StatesGroup):
    waiting_for_first_name = State()
    waiting_for_last_name = State()
    waiting_for_email = State()
    waiting_for_position = State()

def register_user_creation_handlers(dp: Dispatcher):
    @dp.message_handler(Text(equals="Создать пользователя в Bitrix"))
    async def create_user(message: types.Message):
        await message.answer("Введите имя пользователя:")
        await UserCreationForm.waiting_for_first_name.set()

    @dp.message_handler(state=UserCreationForm.waiting_for_first_name)
    async def process_first_name(message: types.Message, state: FSMContext):
        await state.update_data(first_name=message.text)
        await message.answer("Введите фамилию пользователя:")
        await UserCreationForm.waiting_for_last_name.set()

    @dp.message_handler(state=UserCreationForm.waiting_for_last_name)
    async def process_last_name(message: types.Message, state: FSMContext):
        await state.update_data(last_name=message.text)
        await message.answer("Введите email пользователя:")
        await UserCreationForm.waiting_for_email.set()

    @dp.message_handler(state=UserCreationForm.waiting_for_email)
    async def process_email(message: types.Message, state: FSMContext):
        email = message.text
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            await message.answer("Некорректный email адрес. Пожалуйста, введите правильный email.")
            return
        await state.update_data(email=email)
        await message.answer("Введите должность пользователя:")
        await UserCreationForm.waiting_for_position.set()

    @dp.message_handler(state=UserCreationForm.waiting_for_position)
    async def process_position(message: types.Message, state: FSMContext):
        user_data = await state.get_data()
        user_data['position'] = message.text
        
        bitrix_user_data = {
            'EMAIL': [{'VALUE': user_data['email'], 'VALUE_TYPE': 'WORK'}],
            'NAME': user_data['first_name'],
            'LAST_NAME': user_data['last_name'],
            'POSITION': user_data['position'],
            'LOGIN': user_data['email']  # Обязательное поле для создания пользователя
        }
        
        logging.info(f"Передаваемые данные для Bitrix: {bitrix_user_data}")

        result = await create_user_in_bitrix(bitrix_user_data)
        if result:
            await message.answer("Пользователь успешно создан в Bitrix!")
        else:
            await message.answer("Ошибка при создании пользователя в Bitrix.")
        
        await state.finish()
