import logging
from datetime import datetime, timedelta, date, time as dtime
from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from utils.bitrix import booking_add, booking_get
from handlers.common import start_command  

ROOMS = {
    "Комната 1": "11",
    "Комната 2": "13",  
    "Комната 3": "15",
    "Комната 4": "17"
}

class BookingState(StatesGroup):
    selecting_room = State()
    selecting_time = State()
    confirming_booking = State()

def booking_user_handlers(dp: Dispatcher):
    dp.register_callback_query_handler(handle_booking_request, lambda c: c.data == "Забронировать место")
    dp.register_callback_query_handler(process_room_selection, state=BookingState.selecting_room)
    dp.register_callback_query_handler(process_date, state=BookingState.selecting_time)
    dp.register_callback_query_handler(process_time, state=BookingState.confirming_booking)

async def handle_booking_request(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.message.answer("Выберите переговорную комнату:", reply_markup=create_inline_keyboard_rooms())
    await BookingState.selecting_room.set()
    await callback_query.answer()

def create_inline_keyboard_rooms():
    keyboard = InlineKeyboardMarkup(row_width=1)
    buttons = [InlineKeyboardButton(text=name, callback_data=name) for name in ROOMS.keys()]
    buttons.append(InlineKeyboardButton(text="Назад", callback_data="back_to_main"))
    keyboard.add(*buttons)
    return keyboard

def create_inline_keyboard_dates():
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton(text="Сегодня", callback_data="today"),
        InlineKeyboardButton(text="Завтра", callback_data="tomorrow"),
        InlineKeyboardButton(text="Назад", callback_data="back_to_rooms")
    )
    return keyboard

def create_inline_keyboard_times(available_times):
    keyboard = InlineKeyboardMarkup(row_width=3)
    for time in available_times:
        keyboard.insert(InlineKeyboardButton(text=time, callback_data=time))
    keyboard.add(InlineKeyboardButton(text="Назад", callback_data="back_to_dates"))
    return keyboard

async def process_room_selection(callback_query: types.CallbackQuery, state: FSMContext):
    if callback_query.data == "back_to_main":
        await state.finish()
        await start_command(callback_query.message)
        await callback_query.answer()
        return
    
    await state.update_data(room=callback_query.data)
    keyboard = create_inline_keyboard_dates()
    await callback_query.message.answer("Выберите день для бронирования:", reply_markup=keyboard)
    await BookingState.selecting_time.set()
    await callback_query.answer()

async def process_date(callback_query: types.CallbackQuery, state: FSMContext):
    if callback_query.data == "back_to_rooms":
        keyboard = create_inline_keyboard_rooms()
        await callback_query.message.answer("Выберите переговорную комнату:", reply_markup=keyboard)
        await BookingState.selecting_room.set()
        await callback_query.answer()
        return

    await state.update_data(date=callback_query.data)
    data = await state.get_data()
    room = data.get('room')
    date_choice = data.get('date')

    selected_date = date.today() if date_choice == 'today' else date.today() + timedelta(days=1)
    start_time = datetime.combine(selected_date, dtime(0, 0))
    end_time = datetime.combine(selected_date, dtime(23, 59))

    event_data = {
        'type': 'location',
        'ownerId': '0',
        'from': start_time.strftime('%Y-%m-%d %H:%M:%S'),
        'to': end_time.strftime('%Y-%m-%d %H:%M:%S'),
        'section': ROOMS[room]
    }

    response = await booking_get(event_data)

    if isinstance(response, dict) and 'result' in response:
        events = response.get('result', [])
        busy_times = [event['DATE_FROM'][11:16] for event in events]
        available_times = [f"{hour}:00" for hour in range(10, 19) if f"{hour}:00" not in busy_times]
        keyboard = create_inline_keyboard_times(available_times)
        await callback_query.message.answer("Выберите время для бронирования:", reply_markup=keyboard)
        await BookingState.confirming_booking.set()
    else:
        logging.error(f"Ошибка при получении событий: {response}")
        await callback_query.message.answer("Ошибка при получении событий, попробуйте позже.")

    await callback_query.answer()

async def process_time(callback_query: types.CallbackQuery, state: FSMContext):
    if callback_query.data == "back_to_dates":
        keyboard = create_inline_keyboard_dates()
        await callback_query.message.answer("Выберите день для бронирования:", reply_markup=keyboard)
        await BookingState.selecting_time.set()
        await callback_query.answer()
        return

    data = await state.get_data()
    room = data.get('room')
    date_choice = data.get('date')
    time = callback_query.data

    selected_date = date.today() if date_choice == 'today' else date.today() + timedelta(days=1)
    start_time = datetime.combine(selected_date, datetime.strptime(time, '%H:%M').time())
    end_time = start_time + timedelta(hours=1) 

    event_data = {
        'type': 'location',
        'ownerId': '0',
        'name': f"Бронирование переговорки {room}",
        'from': start_time.strftime('%Y-%m-%d %H:%M:%S'),
        'to': end_time.strftime('%Y-%m-%d %H:%M:%S'),
        'section': ROOMS[room],
        'resource': room 
    }

    response = await booking_add(event_data)

    if response is not None and 'result' in response:
        await callback_query.message.answer("Бронирование успешно завершено!")
    else:
        logging.error(f"Ошибка при бронировании: {response}")
        await callback_query.message.answer("Ошибка при бронировании, попробуйте позже.")

    await state.finish()
    await start_command(callback_query.message)  
    await callback_query.answer()

def register_booking_handlers(dp: Dispatcher):
    dp.register_callback_query_handler(process_room_selection, state=BookingState.selecting_room)
    dp.register_callback_query_handler(process_date, state=BookingState.selecting_time)
    dp.register_callback_query_handler(process_time, state=BookingState.confirming_booking)
