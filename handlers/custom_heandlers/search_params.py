from config_data.config import YES, NO
from utils.ru_calendar import MyStyleCalendar, STEPS
from database.db import history_write
from datetime import date, datetime, timedelta
from keyboards.inline.city_confirm import city_markup
from keyboards.reply.keyboards import amt_pics, yes_no, blanc, amt_hotels
from telebot.types import ReplyKeyboardRemove, InputMediaPhoto, Message, CallbackQuery
from rapidapi import requester
from loguru import logger
from loader import bot
from states.search_info import SearchInfoState
import re
logger.add('debug.log', format='{time} {level} {message}', level='DEBUG')


@bot.callback_query_handler(func=MyStyleCalendar.func(calendar_id=1))
def cal(c: CallbackQuery) -> None:
    """Функция, создающая календарь для выбора даты заезда в отель. Отправляет запрос с выбором года.
    Запрашивает месяц и день. Сохраняет информацию
    о дате заезда в словарь с ключом 'check_in'."""
    result, key, step = MyStyleCalendar(
        calendar_id=1, locale='ru', min_date=date.today(), max_date=date.today() + timedelta(days=365)
    ).process(c.data)
    if not result and key:
        bot.edit_message_text(f"Выбери {STEPS[step]}",
                              c.message.chat.id,
                              c.message.message_id,
                              reply_markup=key)
    elif result:
        with bot.retrieve_data(c.message.chat.id) as data:
            data['check_in'] = str(result)
        bot.edit_message_text(f"Выбрано {result}",
                              c.message.chat.id,
                              c.message.message_id)
        bot.send_message(c.message.chat.id, 'Верно?', reply_markup=yes_no())


@bot.callback_query_handler(func=MyStyleCalendar.func(calendar_id=2))
def cal(c: CallbackQuery) -> None:
    """Функция, создающая календарь для выбора даты выезда из отеля. Отправляет запрос с выбором года.
        Запрашивает месяц и день. Сохраняет информацию
        о дате заезда в словарь с ключом 'check_out'."""
    with bot.retrieve_data(c.message.chat.id) as data:
        min_date = datetime.strptime(data['check_in'], "%Y-%m-%d").date() + timedelta(days=1)
        result, key, step = MyStyleCalendar(
            calendar_id=2, locale='ru', min_date=min_date, max_date=min_date + timedelta(days=27)
        ).process(c.data)
    if not result and key:
        bot.edit_message_text(f"Выбери {STEPS[step]}",
                              c.message.chat.id,
                              c.message.message_id,
                              reply_markup=key)
    elif result:
        with bot.retrieve_data(c.message.chat.id) as data:
            data['check_out'] = str(result)
        bot.edit_message_text(f"Выбрано {result}",
                              c.message.chat.id,
                              c.message.message_id)
        bot.send_message(c.message.chat.id, 'Верно?', reply_markup=yes_no())


@bot.callback_query_handler(func=lambda call: True)
def city_conf(call: CallbackQuery) -> None:
    if bot.get_state(call.from_user.id) == SearchInfoState.city:
        with bot.retrieve_data(call.from_user.id) as data:
            for city in data['cities']:
                if city['destination_id'] == call.data:
                    data['city'] = city['city_name']
                    data['city_id'] = call.data
                    bot.send_message(call.from_user.id, f'Выбрано {city["city_name"]}')
        bot.set_state(call.from_user.id, SearchInfoState.hotels_amt)
        bot.answer_callback_query(call.id)
        bot.send_message(call.from_user.id, 'Сколько отелей показать?', reply_markup=amt_hotels())


def my_calendar(message: Message, cur_date=None) -> None:
    """Функция, создающая календарь дат заезда и выезда с разницей в один день."""
    if cur_date:
        calendar, step = MyStyleCalendar(
            calendar_id=2, locale='ru',
            min_date=datetime.strptime(cur_date, "%Y-%m-%d").date() + timedelta(days=1),
            max_date=datetime.strptime(cur_date, "%Y-%m-%d").date() + timedelta(days=27)).build()
        bot.send_message(message.from_user.id, 'Укажи дату выезда', reply_markup=blanc())
        bot.send_message(message.chat.id, f'Выбери {STEPS[step]}', reply_markup=calendar)
    else:
        calendar, step = MyStyleCalendar(
            calendar_id=1, locale='ru',
            min_date=date.today(), max_date=date.today() + timedelta(days=365)).build()
        bot.send_message(message.from_user.id, 'Укажи дату заезда', reply_markup=blanc())
        bot.send_message(message.chat.id, f'Выбери {STEPS[step]}', reply_markup=calendar)


@bot.message_handler(state=SearchInfoState.city)
def city_find(message: Message) -> None:
    """Функция получения информации о названии населенного пункта. Вызывает функцию city_markup и выводит клавиатуру
        с вариантами найденными на rapidapi. Сохраняет информацию о введенном населенном пункте пользователем в виде строки
        в словарь c ключом 'cities'."""
    cities = requester.get_city_id(message.text)
    if cities:
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['cities'] = cities
        bot.send_message(message.from_user.id, 'Уточни, пожалуйста', reply_markup=city_markup(message.text))
    else:
        bot.send_message(message.from_user.id, 'Не удалось найти такой город...\nВ каком городе теперь ищем?')


@bot.message_handler(state=SearchInfoState.hotels_amt)
def hotels_amt(message: Message) -> None:
    """Функция принимает сообщение с количеством отелей и сохраняет в словарь с ключом ''hotels_amt''.
        Отправляет запрос в виде клавиатуры о необходимости вывода фото."""
    if message.text.isdigit():
        if 0 < int(message.text) <= 10:
            with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
                data['hotels_amt'] = int(message.text)
            bot.set_state(message.from_user.id, state=SearchInfoState.pics_need)
            bot.send_message(message.from_user.id, 'Отображать фото?', reply_markup=yes_no())
        else:
            bot.send_message('Введи число от 1 до 10')
    else:
        bot.send_message('Не похоже на число')


@bot.message_handler(state=SearchInfoState.pics_need)
def pics_need(message: Message) -> None:
    """Функция принимает информацию о необходимости вывода фотографий.
       При необходимости вывода отправляет сообщение с запросом количества фотографий."""
    if message.text.lower() in YES:
        bot.set_state(message.from_user.id, state=SearchInfoState.pics_amt)
        bot.send_message(message.from_user.id, 'Сколько фото отображать?', reply_markup=amt_pics())
    elif message.text.lower() in NO:
        bot.set_state(message.from_user.id, state=SearchInfoState.check_in)
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['pics_amt'] = None
        my_calendar(message)
    else:
        bot.send_message(message.from_user.id, 'Так да или нет?')


@bot.message_handler(state=SearchInfoState.pics_amt)
def pics_amt(message: Message) -> None:
    """Функция принимает сообщение о количестве фотографий и сохраняет в словарь с ключом 'pics_amt'."""
    if message.text.isdigit():
        if 0 < int(message.text) <= 5:
            with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
                data['pics_amt'] = int(message.text)
            bot.set_state(message.from_user.id, state=SearchInfoState.check_in)
            my_calendar(message)
        else:
            bot.send_message('Введи число от 1 до 10')
    else:
        bot.send_message('Не похоже на число')


@bot.message_handler(state=SearchInfoState.check_in)
def check_in(message: Message) -> None:
    """Функция, проверяющая правильность ввода даты заезда."""
    date_string = True
    with bot.retrieve_data(message.from_user.id) as data:
        try:
            if not re.fullmatch(r'\d{4}-\d{2}-\d{2}', data['check_in']):
                date_string = False
            else:
                min_date = data['check_in']
        except KeyError:
            date_string = False
    if not date_string:
        bot.send_message(message.from_user.id, 'Неверный ввод! Используй календарь!')
    if message.text.lower() in YES and date_string:
        bot.set_state(message.from_user.id, state=SearchInfoState.check_out)
        my_calendar(message, min_date)
    elif message.text.lower() in NO or not date_string:
        my_calendar(message)
    else:
        bot.send_message(message.from_user.id, 'Так да или нет?')


@bot.message_handler(state=SearchInfoState.check_out)
def check_out(message: Message) -> None:
    """Функция, проверяющая правильность ввода даты выезда."""
    date_string = True
    with bot.retrieve_data(message.from_user.id) as data:
        try:
            if not re.fullmatch(r'\d{4}-\d{2}-\d{2}', data['check_out']):
                date_string = False
            else:
                min_date = data['check_in']
        except KeyError:
            date_string = False
    if not date_string:
        bot.send_message(message.from_user.id, 'Неверный ввод! Используй календарь!')
    if message.text.lower() in YES:
        bot.set_state(message.from_user.id, state=None)
        result_to_chat(message=message)
    elif message.text.lower() in NO:
        my_calendar(message, min_date)
    else:
        bot.send_message(message.from_user.id, 'Так да или нет?')


def result_to_chat(message: Message) -> None:
    """Функция, формирующая словарь с количеством отелей, id и полной информацией в соответствии с запросом
     пользователя. Сохраняет в словарь с ключом ''user_id' и вызывает функцию 'history_write' для записи в
     базу данных."""
    bot.send_message(message.from_user.id, 'Начинаю поиск...', reply_markup=ReplyKeyboardRemove())
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['user_id'] = message.from_user.id
        res = requester.get_hotels(data)
    if len(res) > 0:
        name_list = list()
        for value in res.values():
            if value.get('pics'):
                caption = f'{value["name"]}\n{value["site"]}'
                photos = list()
                for photo in value['pics']:
                    photos.append(InputMediaPhoto(media=photo, caption=caption))
                bot.send_media_group(message.chat.id, photos, disable_notification=True)
            text = f'Название: {value["name"]}\nРейтинг отеля: {value["star_rating"]}\nАдрес: {value["address"]}\n'\
                   f'Расстояние до центра: {value["distance"]}\nЦена за ночь: {value["price_per_night"]} RUB\n'\
                   f'Общая сумма: {value["price_per_stay"]} RUB\n{value["site"]}'
            name_list.append(value["name"])
            bot.send_message(message.from_user.id, text)
        if len(res) == data['hotels_amt']:
            bot.send_message(message.from_user.id, 'Поиск окончен! Что дальше? Выбери команду')
        else:
            bot.send_message(message.from_user.id, 'Это всё, что удалось найти...')
        history_write(data, name_list)
    else:
        bot.send_message(message.from_user.id, 'Ничего не нашёл! Попробуй изменить параметры поиска.')
