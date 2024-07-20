import aiohttp
import logging
from config import BITRIX_WEBHOOK_URL
import requests
import json


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

async def check_email_exists_in_bitrix(email):
    async with aiohttp.ClientSession() as session:
        try:
            url = f"{BITRIX_WEBHOOK_URL}/user.get"
            params = {'filter[EMAIL]': email.strip()}
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
    async with aiohttp.ClientSession() as session:
        try:
            url = f"{BITRIX_WEBHOOK_URL}/user.add"
            data = user_info
            logging.debug(f"Данные для Bitrix: {data}")
            async with session.post(url, json=data) as response:
                response_data = await response.json()
                if response.status != 200 or 'error' in response_data:
                    logging.error(f"Ошибка при добавлении пользователя в Bitrix: {response.status} - {response_data}")
                    return False
                return True
        except Exception as e:
            logging.error(f"Ошибка при запросе к Bitrix: {e}")
            return False