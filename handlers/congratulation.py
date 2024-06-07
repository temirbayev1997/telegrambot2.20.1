import logging
from aiogram import Dispatcher, types
from aiogram.dispatcher.filters import Text
from datetime import datetime
from dateutil.parser import parse as parse_date
import io
from utils.bitrix import get_users_from_bitrix
from utils.pdf import photo_to_pdf

def register_congratulation_handlers(dp: Dispatcher):
    @dp.message_handler(Text(equals="Поздравить пользователя"))
    async def congratulate_user(message: types.Message):
        users = await get_users_from_bitrix()
        if users:
            today = datetime.today().date()
            congratulated = False
            for user in users['result']:
                if 'PERSONAL_BIRTHDAY' in user and user['PERSONAL_BIRTHDAY']:
                    try:
                        user_birthday = parse_date(user['PERSONAL_BIRTHDAY']).date()
                    except Exception as e:
                        logging.error(f"Ошибка обработки даты рождения пользователя: {e}")
                        continue
                    if user_birthday == today:
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