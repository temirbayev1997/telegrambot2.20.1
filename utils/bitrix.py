import aiohttp
import logging
from config import BITRIX_WEBHOOK_URL
from datetime import datetime, timedelta

# import requests
# import json

async def book_meeting_room(room, start_time, end_time):
    async with aiohttp.ClientSession() as session:
        data = {
            "fields": {
                "NAME": f"Бронирование {room}",
                "DESCRIPTION": f"Бронирование переговорной {room} с {start_time} до {end_time}",
                "OWNERID": 0,  
                "FROM": f"2024-07-04T{start_time}:00Z",
                "TO": f"2024-07-04T{end_time}:00Z",  
                "TYPE": "location",
                "SECTION": 24,
                "IS_MEETING":"Y",
                "host": 1
            }
        }
        async with session.post(f"{BITRIX_WEBHOOK_URL}/calendar.event.add", json=data) as response:
            result = await response.json()
            return result

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

async def get_users_from_bitrix():
    async with aiohttp.ClientSession(trust_env=True) as session:
        async with session.get(f"{BITRIX_WEBHOOK_URL}/user.get") as response:
            # response = requests.get(f"{BITRIX_WEBHOOK_URL}/user.get")
            if response.status == 200:
                data = await response.json()
                return data
            else:
                logging.error(f"Ошибка при получении пользователей из Bitrix: {response.status} - {response.reason}")
                return None

async def get_user_fields():
    async with aiohttp.ClientSession(trust_env=True) as session:
        async with session.get(f"{BITRIX_WEBHOOK_URL}/user.fields") as response:
            if response.status == 200:
                data = await response.json()
                return data
            else:
                logging.error(f"Ошибка при получении полей пользователей из Bitrix: {response.status} - {response.reason}")
                return None

async def check_email_exists_in_bitrix(email):
    async with aiohttp.ClientSession(trust_env=True) as session:
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
    async with aiohttp.ClientSession(trust_env=True) as session:
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
        
def find_free_slots(work_start, work_end, events, min_duration=45, max_duration=60):
    occupied_slots = [(datetime.strptime(event['DATE_FROM'], '%Y-%m-%dT%H:%M:%S'), datetime.strptime(event['DATE_TO'], '%Y-%m-%dT%H:%M:%S')) for event in events]
    
    free_slots = []
    
    current_start = work_start
    
    for start, end in sorted(occupied_slots):
        if start > current_start:
            duration = (start - current_start).total_seconds() / 60
            if min_duration <= duration <= max_duration:
                free_slots.append((current_start, start))
        current_start = max(current_start, end)
    
    if current_start < work_end:
        duration = (work_end - current_start).total_seconds() / 60
        if min_duration <= duration <= max_duration:
            free_slots.append((current_start, work_end))
    
    return free_slots