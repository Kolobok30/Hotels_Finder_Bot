from telebot.types import ReplyKeyboardMarkup, KeyboardButton


def amt_hotels() -> ReplyKeyboardMarkup:
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keys = []
    for i in range(1, 11):
        key = KeyboardButton(str(i))
        keys.append(key)
    keyboard.add(*keys, row_width=5)
    return keyboard


def yes_no() -> ReplyKeyboardMarkup:
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    key_yes = KeyboardButton('да')
    key_no = KeyboardButton('нет')
    keyboard.add(key_yes, key_no)
    return keyboard


def amt_pics() -> ReplyKeyboardMarkup:
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keys = []
    for i in range(1, 6):
        key = KeyboardButton(str(i))
        keys.append(key)
    keyboard.add(*keys)
    return keyboard


def blanc() -> ReplyKeyboardMarkup:
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(KeyboardButton(' '))
    return keyboard
