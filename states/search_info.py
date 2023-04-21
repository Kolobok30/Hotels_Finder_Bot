from telebot.handler_backends import State, StatesGroup


class SearchInfoState(StatesGroup):
    city = State()
    city_id = State()
    city_confirm = State()
    hotels_amt = State()
    price_min = State()
    price_max = State()
    dist_min = State()
    dist_max = State()
    pics_need = State()
    pics_amt = State()
    check_in = State()
    check_out = State()
    history = State()

