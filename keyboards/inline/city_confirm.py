from rapidapi.requester import get_city_id


from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton


def city_markup(name_city: str) -> InlineKeyboardMarkup:
    """Вызывает функцию get_city_id и возвращает клавиатуру с кнопками содержащими найденные варианты по запросу"""
    cities = get_city_id(name_city)
    destinations = InlineKeyboardMarkup()
    if cities:
        for city in cities:
            destinations.add(InlineKeyboardButton(text=city['city_name'],
                                                  callback_data=city['destination_id']))
        return destinations
    else:
        return None



# def city_markup(cities) -> InlineKeyboardMarkup:
#     """Возвращает клавиатуру с кнопками содержащими найденные варианты по запросу"""
#     destinations = InlineKeyboardMarkup()
#     if cities:
#         for city in cities:
#             destinations.add(InlineKeyboardButton(text=city['city_name'],
#                                                   callback_data=city['destination_id']))
#             return destinations
#     else:
#         return None
