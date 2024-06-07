import aiohttp
import logging
from config import BITRIX_WEBHOOK_URL

async def get_users_from_bitrix():
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{BITRIX_WEBHOOK_URL}/user.get") as response:
            if response.status == 200:
                data = await response.json()
                return data
            else:
                logging.error(f"Ошибка при получении пользователей из Bitrix: {response.status} - {response.reason}")
                return None

# async def get_user_fields():
#     async with aiohttp.ClientSession() as session:
#         async with session.get(f"{BITRIX_WEBHOOK_URL}/user.fields") as response:
#             if response.status == 200:
#                 data = await response.json()
#                 return data
#             else:
#                 logging.error(f"Ошибка при получении полей пользователей из Bitrix: {response.status} - {response.reason}")
#                 return None
            
async def create_user_in_bitrix(user_data):
    async with aiohttp.ClientSession() as session:
        try:
            logging.info(f"Отправка запроса к Bitrix: {BITRIX_WEBHOOK_URL}/user.add с данными: {user_data}")
            async with session.post(f"{BITRIX_WEBHOOK_URL}/user.add", json={'fields': user_data}) as response:
                data = await response.json()
                if response.status != 200 or 'error' in data:
                    logging.error(f"Ошибка при создании пользователя в Bitrix: {response.status} - {data}")
                    return None
                logging.info(f"Пользователь успешно создан в Bitrix: {data}")
                return data
        except Exception as e:
            logging.error(f"Ошибка при запросе к Bitrix: {e}")
            return None