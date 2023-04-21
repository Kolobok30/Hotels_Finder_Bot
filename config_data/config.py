import os
from dotenv import load_dotenv, find_dotenv

if not find_dotenv():
    exit('Переменные окружения не загружены т.к отсутствует файл .env')
else:
    load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
RAPID_API_KEY = os.getenv('RAPID_API_KEY')
HEADERS = {
        'x-rapidapi-host': "hotels4.p.rapidapi.com",
        'x-rapidapi-key': RAPID_API_KEY
          }
DEFAULT_COMMANDS = (
    ('start', "Запустить бота"),
    ('help', "Вывести справку"),
    ('lowprice', "Поиск самых дешёвых отелей в городе"),
    ('highprice', "Поиск самых дорогих отелей в городе"),
    ('bestdeal', "Поиск по цене и расстоянию от центра"),
    ('history', "История поиска")
)
YES = ['да', 'yes']
NO = ['нет', 'no']