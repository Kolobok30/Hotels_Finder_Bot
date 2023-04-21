from loader import bot
from database.db import Result, db
from telebot.types import Message
from states.search_info import SearchInfoState


@bot.message_handler(commands=['lowprice'])
def lowprice(message: Message) -> None:
    """Функция обработчик команды /lowprice. Отправляет пользователю сообщение с запросом названия города."""

    bot.set_state(message.from_user.id, SearchInfoState.city)
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['cmd'] = 'lowprice'
    bot.reply_to(message, 'В каком городе ищем?')


@bot.message_handler(commands=['highprice'])
def highprice(message: Message) -> None:
    """Функция обработчик команды /highprice. Отправляет пользователю сообщение с запросом названия города."""

    bot.set_state(message.from_user.id, SearchInfoState.city)
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['cmd'] = 'highprice'
    bot.reply_to(message, 'В каком городе ищем?')


@bot.message_handler(commands=['bestdeal'])
def besteal(message: Message) -> None:
    """Функция обработчик команды /bestdeal. Отправляет пользователю сообщение с запросом минимальной цены."""

    bot.set_state(message.from_user.id, SearchInfoState.price_min, message.chat.id)
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['cmd'] = 'bestdeal'
    bot.reply_to(message, 'Укажи минимальную цену')


@bot.message_handler(commands=['history'])
def history(message: Message) -> None:
    """Функция обработчик команды /history. Выводит историю поиска в виде
    команды, которую вводил пользователь, времени ввода команды и найденных отелей."""

    bot.set_state(message.from_user.id, SearchInfoState.history, message.chat.id)
    with db:
        if Result.select().where(Result.user_id == message.from_user.id).count() > 0:
            text = ''
            for result in Result.select().where(Result.user_id == message.from_user.id):
                text += f'{result.date}\nКоманда: {result.command}\nОтели:\n{result.result}\n\n'
            bot.reply_to(message, text)
        else:
            bot.reply_to(message, 'История поиска пуста')
