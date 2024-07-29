import io, logging, requests

from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import InputFile

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from handlers.common import start_command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from PIL import Image

class Form(StatesGroup):
    waiting_for_photo_url = State()

def register_photo_handlers(dp: Dispatcher):
    logging.info("Registering photo handlers...")

    @dp.callback_query_handler(lambda c: c.data == 'Загрузить фото')
    async def handle_upload_photo(callback_query: types.CallbackQuery):
        keyboard = InlineKeyboardMarkup().add(InlineKeyboardButton(text="Отмена", callback_data="cancel"))
        await callback_query.message.answer("Отправьте ссылку на изображение или нажмите 'Отмена' для выхода.", reply_markup=keyboard)
        await Form.waiting_for_photo_url.set()
        await callback_query.answer()

    @dp.message_handler(state=Form.waiting_for_photo_url, content_types=types.ContentType.TEXT)
    async def handle_image_url(message: types.Message, state: FSMContext):
        if message.text.startswith('http'):
            try:
                response = requests.get(message.text)
                response.raise_for_status() 
                img = Image.open(io.BytesIO(response.content))

                pdf_file = io.BytesIO()
                c = canvas.Canvas(pdf_file, pagesize=letter)
                c.drawInlineImage(img, 0, 0, width=letter[0], height=letter[1])
                c.save()
                pdf_file.seek(0)

                await message.bot.send_document(message.chat.id, InputFile(pdf_file, filename='photo.pdf'))
            except Exception as e:
                logging.error(f"Ошибка загрузки изображения: {e}")
                await message.answer("Произошла ошибка при загрузке изображения.")
            finally:
                await state.finish()
        else:
            await message.answer("Пожалуйста, отправьте корректную ссылку на изображение.")

    @dp.callback_query_handler(lambda c: c.data == 'cancel', state=Form.waiting_for_photo_url)
    async def cancel_upload(callback_query: types.CallbackQuery, state: FSMContext):
        await state.finish()
        await start_command(callback_query.message)
        await callback_query.answer()