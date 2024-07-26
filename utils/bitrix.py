import aiohttp
import logging
from config import BITRIX_WEBHOOK_URL
# import requests
# import json


async def get_users_from_bitrix():
    url = f"{BITRIX_WEBHOOK_URL}/user.get"  # Ensure this endpoint is correct
    async with aiohttp.ClientSession(trust_env=True) as session:
        try:
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    return data
                else:
                    logging.error(f"Ошибка при получении пользователей из Bitrix: {response.status} - {response.reason}")
                    return None
        except Exception as e:
            logging.error(f"Ошибка при запросе к Bitrix: {e}")
            return None

async def get_user_fields():
    url = f"{BITRIX_WEBHOOK_URL}/user.fields"  # Ensure this endpoint is correct
    async with aiohttp.ClientSession(trust_env=True) as session:
        try:
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    return data
                else:
                    logging.error(f"Ошибка при получении полей пользователей из Bitrix: {response.status} - {response.reason}")
                    return None
        except Exception as e:
            logging.error(f"Ошибка при запросе к Bitrix: {e}")
            return None

async def check_email_exists_in_bitrix(email):
    url = f"{BITRIX_WEBHOOK_URL}/user.get"  # Ensure this endpoint is correct
    params = {'filter[EMAIL]': email.strip()}
    async with aiohttp.ClientSession(trust_env=True) as session:
        try:
            async with session.get(url, params=params) as response:
                response_data = await response.json()
                if response.status != 200 or 'error' in response_data:
                    logging.error(f"Ошибка при проверке email в Bitrix: {response.status} - {response_data}")
                    return False
                return bool(response_data['result'])
        except Exception as e:
            logging.error(f"Ошибка при запросе к Bitrix: {e}")
            return False

async def add_user_to_bitrix(user_info):
    url = f"{BITRIX_WEBHOOK_URL}/user.add"  # Ensure this endpoint is correct
    async with aiohttp.ClientSession(trust_env=True) as session:
        try:
            async with session.post(url, json=user_info) as response:
                response_data = await response.json()
                if response.status != 200 or 'error' in response_data:
                    logging.error(f"Ошибка при добавлении пользователя в Bitrix: {response.status} - {response_data}")
                    return False
                return True
        except Exception as e:
            logging.error(f"Ошибка при запросе к Bitrix: {e}")
            return False
        
async def booking_get(user_info):
    url = f"{BITRIX_WEBHOOK_URL}/calendar.event.get"
    async with aiohttp.ClientSession(trust_env=True) as session:
        try:
            async with session.post(url, json=user_info) as response:
                response_data = await response.json()
                if response.status != 200 or 'error' in response_data:
                    logging.error(f"Error: {response.status} - {response_data}")
                    return False
                return response_data
        except Exception as e:
            logging.error(f"Error: {e}")
            return False

async def booking_add(event_data):
    url = f"{BITRIX_WEBHOOK_URL}/calendar.event.add"
    async with aiohttp.ClientSession(trust_env=True) as session:
        try:
            async with session.post(url, json=event_data) as response:
                response_data = await response.json()
                if response.status != 200 or 'error' in response_data:
                    logging.error(f"Ошибка: {response.status} - {response_data}")
                    return {'status_code': response.status, 'text': response_data}
                return {'status_code': response.status, 'result': response_data}
        except Exception as e:
            logging.error(f"Ошибка: {e}")
            return {'status_code': None, 'text': str(e)}


