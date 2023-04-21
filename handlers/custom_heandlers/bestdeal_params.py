from loguru import logger
from loader import bot
from telebot.types import Message
from states.search_info import SearchInfoState
logger.add('debug.log', format='{time} {level} {message}', level='DEBUG')


@bot.message_handler(state=SearchInfoState.price_min)
def price_min(message: Message) -> None:
    """Принимает минимальную стоимость и отправляет запрос о максимальной стоимости"""
    if message.text.isdigit():
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['price_min'] = int(message.text)
        bot.set_state(message.from_user.id, SearchInfoState.price_max, message.chat.id)
        bot.send_message(message.from_user.id, 'Укажи максимальную цену')
    else:
        bot.send_message(message.from_user.id, 'Ошибка ввода. Введи целое число цифрами')


@bot.message_handler(state=SearchInfoState.price_max)
@logger.catch
def price_max(message: Message) -> None:
    """Принимает максимальную стоимость и отправляет запрос о минимальном расстоянии от центра"""
    if message.text.isdigit():
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['price_max'] = int(message.text)
        bot.set_state(message.from_user.id, SearchInfoState.dist_min, message.chat.id)
        bot.send_message(message.from_user.id, 'Укажи минимальное расстояние от центра(км)')
    else:
        bot.send_message(message.from_user.id, 'Ошибка ввода. Введи целое число цифрами')


@bot.message_handler(state=SearchInfoState.dist_min)
@logger.catch
def get_distance_min(message: Message) -> None:
    """Принимает минимальное расстояние от центра и отправляет запрос о максимальном расстоянии"""
    if message.text.isdigit():
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['dist_min'] = int(message.text)
        bot.set_state(message.from_user.id, SearchInfoState.dist_max, message.chat.id)
        bot.send_message(message.from_user.id, 'Укажи максимальное расстояние от центра(км)')
    else:
        bot.send_message(message.from_user.id, 'Ошибка ввода. Введи целое число цифрами')


@bot.message_handler(state=SearchInfoState.dist_max)
@logger.catch
def get_distance_min(message: Message) -> None:
    """Принимает максимальное расстояние от центра и отправляет сообщение с запросом названия города"""
    if message.text.isdigit():
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['dist_max'] = int(message.text)
        bot.set_state(message.from_user.id, SearchInfoState.city, message.chat.id)
        bot.send_message(message.from_user.id, 'В каком городе ищем?')
    else:
        bot.send_message(message.from_user.id, 'Ошибка ввода. Введи целое число цифрами')
