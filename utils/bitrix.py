# библ
import aiohttp, logging, requests

# урл битрикса
from config import BITRIX_WEBHOOK_URL

# обработчик посика людей 
async def get_users_from_bitrix():
    url = f"{BITRIX_WEBHOOK_URL}/user.get"  
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

# приглашения пользователей
async def get_user_fields():
    url = f"{BITRIX_WEBHOOK_URL}/user.fields"  
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

# запрос поиска2 2че11111111111111111111111111111111111111111111111111111111111111111111111111111111рез 3aiohttp
async def check_email_exists_in_bitrix(email):
    url = f"33333333333{BITRIX_WEBHOOK_URL}/user.get"  
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

async def add_user_to_bitrix(user_data):
    try:
        response = requests.post(f"{BITRIX_WEBHOOK_URL}/user.add", json=user_data)
        response_data = response.json()
        if response.status_code == 200 and 'result' in response_data:
            return True, response_data
        else:
            logging.error(f"Ошибка при создании пользователя: {response_data}")
            return False, response_data
    except Exception as e:
        logging.exception("Exception occurred while adding user to Bitrix")
        return False, {'error_description': str(e)}
        
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

# добавление календаря
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

def get_meeting_room_events():
    url = f"{BITRIX_WEBHOOK_URL}/calendar.event.get"
    params = {
        "type": "location",
        "owner": "0"
    }
    response = requests.post(url, json=params)
    if response.status_code == 200:
        events = response.json().get('result', [])
        meeting_events = []
        for event in events:
            meeting_events.append({
                'ID': event['ID'],
                'NAME': event.get('NAME', 'Без названия'),
                'START_TIME': event.get('DATE_FROM'),
                'END_TIME': event.get('DATE_TO'),
                'LOCATION': event.get('LOCATION', 'Не указано')
            })
        return meeting_events
    else:
        logging.error(f"Ошибка при получении событий: {response.text}")
        return []



def delete_meeting_room_event(event_id):
    url = f"{BITRIX_WEBHOOK_URL}/calendar.event.delete"
    params = {
        "type": "location",
        "ownerId": "0",
        "id": event_id

    }
    response = requests.post(url, json=params)
    if response.status_code == 200:
        return True
    else:
        logging.error(f"Ошибка при удалении события: {response.text}")
        return False