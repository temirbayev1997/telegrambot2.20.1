import aiohttp
import logging
import re
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

async def get_user_fields():
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{BITRIX_WEBHOOK_URL}/user.fields") as response:
            if response.status == 200:
                data = await response.json()
                return data
            else:
                logging.error(f"Ошибка при получении полей пользователей из Bitrix: {response.status} - {response.reason}")
                return None
            
async def add_user_to_bitrix(user_data):
    email = user_data['email']
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        logging.error(f"Некорректный email адрес: {email}")
        return False

    payload = {
        'fields': {
            'EMAIL': [{'VALUE': email.strip(), 'VALUE_TYPE': 'WORK'}],
            'NAME': user_data['first_name'],
            'LAST_NAME': user_data['last_name'],
            'POSITION': user_data['position'],
            'DEPARTMENT': [int(user_data['department'])],
            'ACTIVE': 'Y',
            'PASSWORD': 'some_secure_password',
            'EXTRANET': 'N'
        }
    }

    logging.info(f"Отправка запроса к Bitrix: {BITRIX_WEBHOOK_URL}/user.add с данными: {payload}")
    async with aiohttp.ClientSession() as session:
        async with session.post(f"{BITRIX_WEBHOOK_URL}/user.add", json=payload) as response:
            if response.status == 200:
                logging.info("Пользователь успешно создан в Bitrix.")
                return True
            else:
                response_data = await response.json()
                logging.error(f"Ошибка при создании пользователя в Bitrix: {response.status} - {response_data}")
                return False

async def check_email_exists_in_bitrix(email):
    async with aiohttp.ClientSession() as session:
        try:
            url = f"{BITRIX_WEBHOOK_URL}/user.get"
            params = {'filter': {'EMAIL': email}}
            async with session.get(url, params=params) as response:
                response_data = await response.json()
                if response.status != 200 or 'error' in response_data:
                    logging.error(f"Ошибка при проверке email в Bitrix: {response.status} - {response_data}")
                    return False
                return bool(response_data['result'])
        except Exception as e:
            logging.error(f"Ошибка при запросе к Bitrix: {e}")
            return False
