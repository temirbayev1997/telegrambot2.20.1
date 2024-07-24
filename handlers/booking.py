import logging
from utils.bitrix import book_meeting_room
from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup

class BookingState(StatesGroup):
    selecting_room = State()
    selecting_time = State()
    confirming_booking = State()

def register_booking_handlers(dp: Dispatcher):
    dp.register_callback_query_handler(start_booking, Text(equals="Забронировать место"))
    dp.register_callback_query_handler(process_room_selection, Text(startswith="book_room_"), state=BookingState.selecting_room)
    dp.register_callback_query_handler(process_time_selection, Text(startswith="select_time_"), state=BookingState.selecting_time)
    dp.register_message_handler(confirm_booking, state=BookingState.confirming_booking)

async def start_booking(callback_query: types.CallbackQuery):
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text="Переговорная 1", callback_data="book_room_1"))
    keyboard.add(types.InlineKeyboardButton(text="Переговорная 2", callback_data="book_room_2"))
    await callback_query.message.answer("Выберите переговорную:", reply_markup=keyboard)
    await BookingState.selecting_room.set()
    await callback_query.answer()

async def process_room_selection(callback_query: types.CallbackQuery, state: FSMContext):
    room = callback_query.data.split("_")[2]
    await state.update_data(room=room)
    
    # Выбор времени
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text="17:00-17:50", callback_data="select_time_17:00-17:50"))
    keyboard.add(types.InlineKeyboardButton(text="17:55-18:45", callback_data="select_time_17:55-18:45"))
    await callback_query.message.answer(f"Вы выбрали переговорную: {room}. Выберите время:", reply_markup=keyboard)
    await BookingState.selecting_time.set()
    await callback_query.answer()

async def process_time_selection(callback_query: types.CallbackQuery, state: FSMContext):
    time_slot = callback_query.data.split("_")[2]
    await state.update_data(time_slot=time_slot)
    await callback_query.message.answer(f"Вы выбрали время: {time_slot}. Подтвердите бронирование (да/нет):")
    await BookingState.confirming_booking.set()
    await callback_query.answer()

async def confirm_booking(message: types.Message, state: FSMContext):
    if message.text.lower() == "да":
        data = await state.get_data()
        room = data['room']
        time_slot = data['time_slot']
        start_time, end_time = time_slot.split('-')
        try:
            # Логируем данные для бронирования
            logging.debug(f"Попытка бронирования: Комната - {room}, Время - {start_time}-{end_time}")
            # Вызов функции бронирования
            result = await book_meeting_room(room, start_time, end_time)
            logging.info(f"Результат бронирования: {result}")
            await message.answer(f"Переговорная {room} успешно забронирована с {start_time} до {end_time}.")
        except Exception as e:
            logging.error(f"Ошибка при бронировании: {e}")
            await message.answer("Произошла ошибка при бронировании. Попробуйте позже.")
    else:
        await message.answer("Бронирование отменено.")
    await state.finish()
