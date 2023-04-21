from telegram_bot_calendar import DetailedTelegramCalendar

STEPS = {'y': 'год', 'm': 'месяц', 'd': 'день'}


class MyStyleCalendar(DetailedTelegramCalendar):
    """Класс календаря для кастомизации"""
    size_year_column = 1
    prev_button = "⬅️"
    next_button = "➡️"
    empty_month_button = ""