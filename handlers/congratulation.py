import logging, io
from aiogram import Dispatcher, types
from datetime import datetime
from dateutil.parser import parse as parse_date
from utils.bitrix import get_users_from_bitrix
from utils.pdf import photo_to_pdf

def register_congratulation_handlers(dp: Dispatcher):
    dp.register_callback_query_handler(handle_inline_buttons, lambda c: c.data == "Поздравить пользователя")

async def handle_inline_buttons(callback_query: types.CallbackQuery):
    await congratulate_user(callback_query.message)
    await callback_query.answer()

async def congratulate_user(message: types.Message):
    users = await get_users_from_bitrix()
    if users:
        today = datetime.today()
        today_day_month = (today.day, today.month)  
        congratulated = False
        for user in users['result']:
            if 'PERSONAL_BIRTHDAY' in user and user['PERSONAL_BIRTHDAY']:
                try:
                    user_birthday = parse_date(user['PERSONAL_BIRTHDAY'])
                    user_day_month = (user_birthday.day, user_birthday.month)  
                except Exception as e:
                    logging.error(f"Ошибка обработки даты рождения пользователя: {e}")
                    continue
                if user_day_month == today_day_month: 
                    photo_url = user.get('PERSONAL_PHOTO')
                    if photo_url:
                        pdf_bytes = io.BytesIO()
                        await photo_to_pdf(photo_url, pdf_bytes)
                        pdf_bytes.seek(0)
                        await message.bot.send_document(
                            message.chat.id,
                            types.InputFile(pdf_bytes, filename='birthday_photo.pdf'),
                            caption="Happy birthday"
                        )
                    congratulated = True
        if congratulated:
            await message.answer("Пользователи поздравлены")
        else:
            await message.answer("Сегодня нет пользователей с днем рождения")
    else:
        await message.answer("Ошибка при получении пользователей из Bitrix")
