import logging
from datetime import datetime
from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from utils.bitrix import book_meeting_room
from utils.bitrix import find_free_slots
from utils.bitrix import fetch_events
from config import BITRIX_WEBHOOK_URL
import aiohttp


async def fetch_events(start_date, end_date):
    url = f"{BITRIX_WEBHOOK_URL}/calendar.event.list"
    params = {
        'filter[DATE_FROM]': start_date.isoformat(),
        'filter[DATE_TO]': end_date.isoformat(),
        'select[]': ['DATE_FROM', 'DATE_TO']
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params) as response:
            result = await response.json()
            return result.get('result', [])

def find_free_slots(work_start, work_end, events, min_duration=45, max_duration=60):
    occupied_slots = [(datetime.strptime(event['DATE_FROM'], '%Y-%m-%dT%H:%M:%S'), datetime.strptime(event['DATE_TO'], '%Y-%m-%dT%H:%M:%S')) for event in events]
    
    free_slots = []
    
    # Добавляем виртуальный слот перед первым занятым
    current_start = work_start
    
    for start, end in sorted(occupied_slots):
        if start > current_start:
            duration = (start - current_start).total_seconds() / 60
            if min_duration <= duration <= max_duration:
                free_slots.append((current_start, start))
        current_start = max(current_start, end)
    
    # Добавляем виртуальный слот после последнего занятого интервала
    if current_start < work_end:
        duration = (work_end - current_start).total_seconds() / 60
        if min_duration <= duration <= max_duration:
            free_slots.append((current_start, work_end))
    
    return free_slots

class BookingState(StatesGroup):
    selecting_room = State()
    selecting_time = State()
    confirming_booking = State()

def register_booking_handlers(dp: Dispatcher):
    dp.register_callback_query_handler(start_booking, Text(equals="Забронировать место"))
    dp.register_callback_query_handler(process_room_selection, Text(startswith="book_room_"), state=BookingState.selecting_room)
    dp.register_callback_query_handler(process_time_selection, Text(startswith="select_time_"), state=BookingState.selecting_time)
    dp.register_message_handler(confirm_booking, state=BookingState.confirming_booking)
    dp.register_message_handler(show_free_slots, Text(equals="Показать свободные слоты"))

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
    
    # Получаем свободные слоты для выбора времени
    today = datetime.now().date()
    start_date = datetime.combine(today, datetime.min.time())
    end_date = datetime.combine(today, datetime.max.time())
    
    events = await fetch_events(start_date, end_date)
    
    work_start = datetime.combine(today, datetime(2024, 7, 24, 9, 0).time())
    work_end = datetime.combine(today, datetime(2024, 7, 24, 18, 0).time())
    
    free_slots = find_free_slots(work_start, work_end, events)
    
    keyboard = types.InlineKeyboardMarkup()
    for start, end in free_slots:
        button_text = f"{start.strftime('%H:%M')}-{end.strftime('%H:%M')}"
        callback_data = f"select_time_{start.strftime('%H:%M')}-{end.strftime('%H:%M')}"
        keyboard.add(types.InlineKeyboardButton(text=button_text, callback_data=callback_data))
    
    if not free_slots:
        await callback_query.message.answer("Свободных слотов нет.")
    else:
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

async def show_free_slots(message: types.Message):
    today = datetime.now().date()
    start_date = datetime.combine(today, datetime.min.time())
    end_date = datetime.combine(today, datetime.max.time())
    
    events = await fetch_events(start_date, end_date)
    
    work_start = datetime.combine(today, datetime(2024, 7, 24, 9, 0).time())
    work_end = datetime.combine(today, datetime(2024, 7, 24, 18, 0).time())
    
    free_slots = find_free_slots(work_start, work_end, events)
    if not free_slots:
        await message.answer("Свободные слоты не найдены.")
    else:
        slots_message = "\n".join(
            f"Свободный слот: с {start.strftime('%H:%M')} до {end.strftime('%H:%M')}, длительность: {(end - start).total_seconds() / 60:.0f} минут"
            for start, end in free_slots
        )
        await message.answer(f"Свободные слоты:\n{slots_message}")