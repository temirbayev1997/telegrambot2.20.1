from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from utils.bitrix import get_meeting_room_events, delete_meeting_room_event

async def cancel_booking(callback_query: types.CallbackQuery):
    events = get_meeting_room_events()
    if not events:
        await callback_query.message.answer("Нет доступных бронирований для отмены.")
        return
    
    keyboard = InlineKeyboardMarkup()
    for event in events:
        event_id = event['ID']  
        event_name = event['NAME']
        start_time = event['START_TIME']
        event_text = f"{event_name} (с {start_time})"
        keyboard.add(InlineKeyboardButton(text=f"{event_text}", callback_data=f"delete_{event_id}"))
    
    await callback_query.message.answer("Выберите бронирование для отмены:", reply_markup=keyboard)


async def process_delete_booking(callback_query: types.CallbackQuery):
    event_id = callback_query.data.split('_')[1]  
    success = delete_meeting_room_event(event_id)  
    
    if success:
        await callback_query.message.answer(f"Бронирование успешно отменено.")
    else:
        await callback_query.message.answer(f"Ошибка при отмене бронирования.")


def register_del_booking_handlers(dp):
    dp.register_callback_query_handler(cancel_booking, lambda c: c.data == "Отменить бронирвание")
    dp.register_callback_query_handler(process_delete_booking, lambda c: c.data.startswith("delete_"))
