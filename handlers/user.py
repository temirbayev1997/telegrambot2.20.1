from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from utils.bitrix import add_user_to_bitrix, check_email_exists_in_bitrix
import logging
import re
from aiogram.dispatcher.filters import Text

class UserCreationForm(StatesGroup):
    waiting_for_first_name = State()
    waiting_for_last_name = State()
    waiting_for_email = State()
    waiting_for_position = State()
    waiting_for_department = State()

def register_user_creation_handlers(dp: Dispatcher):
    @dp.message_handler(Text(equals="Создать пользователя в Bitrix", ignore_case=True))
    async def create_user(message: types.Message):
        await message.answer("Введите имя пользователя:")
        await UserCreationForm.waiting_for_first_name.set()

    @dp.message_handler(state=UserCreationForm.waiting_for_first_name)
    async def process_first_name(message: types.Message, state: FSMContext):
        first_name = message.text.strip()
        if not first_name.isalpha():
            await message.answer("Имя должно содержать только буквы. Пожалуйста, введите правильное имя.")
            return
        await state.update_data(first_name=first_name)
        await message.answer("Введите фамилию пользователя:")
        await UserCreationForm.waiting_for_last_name.set()

    @dp.message_handler(state=UserCreationForm.waiting_for_last_name)
    async def process_last_name(message: types.Message, state: FSMContext):
        last_name = message.text.strip()
        if not last_name.isalpha():
            await message.answer("Фамилия должна содержать только буквы. Пожалуйста, введите правильную фамилию.")
            return
        await state.update_data(last_name=last_name)
        await message.answer("Введите email пользователя:")
        await UserCreationForm.waiting_for_email.set()

    @dp.message_handler(state=UserCreationForm.waiting_for_email)
    async def process_email(message: types.Message, state: FSMContext):
        email = message.text.strip()
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            await message.answer("Некорректный email адрес. Пожалуйста, введите правильный email.")
            return

        # Проверка уникальности email
        if await check_email_exists_in_bitrix(email):
            await message.answer("Этот email уже используется. Пожалуйста, введите другой email.")
            return

        await state.update_data(email=email)
        await message.answer("Введите должность пользователя:")
        await UserCreationForm.waiting_for_position.set()

    @dp.message_handler(state=UserCreationForm.waiting_for_position)
    async def process_position(message: types.Message, state: FSMContext):
        position = message.text.strip()
        if not position:
            await message.answer("Должность не может быть пустой. Пожалуйста, введите должность.")
            return
        await state.update_data(position=position)
        await message.answer("Введите отдел (номер отдела):")
        await UserCreationForm.waiting_for_department.set()

    @dp.message_handler(state=UserCreationForm.waiting_for_department)
    async def process_department(message: types.Message, state: FSMContext):
        department = message.text.strip()
        if not department.isdigit():
            await message.answer("Отдел должен быть числом. Пожалуйста, введите правильный номер отдела.")
            return

        await state.update_data(department=department)
        
        user_data = await state.get_data()

        logging.info(f"Передаваемые данные для Bitrix: {user_data}")

        result = await add_user_to_bitrix(user_data)
        if result:
            await message.answer("Пользователь успешно создан в Bitrix!")
        else:
            await message.answer("Ошибка при создании пользователя в Bitrix.")
        
        await state.finish()