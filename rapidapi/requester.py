import json
import requests
from config_data.config import HEADERS
from utils.calculate_number_days import calculate_days
import re
from typing import Dict, List
from loguru import logger
logger.add('debug.log', format='{time} {level} {message}', level='DEBUG')


@logger.catch
def request_to_api(url: str, querystring: Dict) -> requests.Response | None:
    """Универсальная функция по отправке запроса на rapidapi."""

    try:
        response = requests.request("GET", url, headers=HEADERS, params=querystring, timeout=30)
        if response.status_code == requests.codes.ok:
            return response
    except requests.exceptions.ReadTimeout:
        return None


@logger.catch
def get_city_id(name: str) -> list | None:
    """Функция формирования и обработки запроса с названием города.
    Возвращает список из словарей с названием найденных
    вариантов и их ID"""

    url = "https://hotels4.p.rapidapi.com/locations/v2/search"
    querystring = {"query": name, "locale": "ru_RU", "currency": "RUB"}
    resp = None
    try_num = 0
    while not resp and try_num < 5:
        resp = request_to_api(url, querystring)
        try_num += 1
    if not resp:
        return None
    pattern = r'(?<="CITY_GROUP",).+?[\]]'
    find = re.search(pattern, resp.text)
    if find:
        suggestions = json.loads(f"{{{find[0]}}}")
        cities = list()
        for dest_id in suggestions['entities']:
            pattern = r'<.*>\S*'
            result_destination = (re.sub(pattern, '', dest_id['caption']))
            if result_destination.find(dest_id['name']) == -1:
                result_destination = ''.join([dest_id['name'], ',', result_destination])
            cities.append({'city_name': result_destination, 'destination_id': dest_id['destinationId']})
        return cities
    else:
        return None


@logger.catch
def get_hotels(data: Dict) -> Dict:
    """Функция формирования и обработки запроса по поиску отелей.
    Возвращает список из словарей с названием найденных
    вариантов и их ID"""
    url = "https://hotels4.p.rapidapi.com/properties/list"
    querystring = querystring_form(data)
    resp = None
    old_resp = None
    result = dict()

    while True:
        try_num = 0
        while resp == old_resp and try_num < 5:
            resp = request_to_api(url, querystring)
            try_num += 1
        if not resp:
            return result

        old_resp = resp
        pattern = r'(?<=,)"results":.+?(?=,"pagination)'
        find = re.search(pattern, resp.text)
        if find:
            suggestions = json.loads(f"{{{find[0]}}}")
            hotels = suggestions["results"]
            result = stringer(hotels, result, data)
            if len(result) == data['hotels_amt']:
                break
            querystring["pageNumber"] = str(int(querystring["pageNumber"]) + 1)
        else:
            break
    return result


@logger.catch
def querystring_form(data: Dict) -> Dict:
    """Функция формирования строки запроса в зависимости от введённой пользователем команды"""
    if data['cmd'] == 'bestdeal':
        querystring = {"destinationId": data['city_id'], "pageNumber": '1', "pageSize": '25',
                       "checkIn": data['check_in'], "checkOut": data['check_out'], "adults1": '1',
                       "priceMin": data['price_min'], "priceMax": data['price_max'],
                       "sortOrder": "DISTANCE_FROM_LANDMARK", "locale": 'ru_RU', "currency": 'RUB',
                       "landmarkIds": "city center"}

    else:
        sort_order = ''
        if data['cmd'] == 'lowprice':
            sort_order = 'PRICE'
        elif data['cmd'] == 'highprice':
            sort_order = 'PRICE_HIGHEST_FIRST'
        querystring = {"destinationId": data['city_id'], "pageNumber": '1', "pageSize": '25',
                       "checkIn": data['check_in'], "checkOut": data['check_out'], "adults1": "1",
                       "sortOrder": sort_order, "locale": "ru_RU", "currency": "RUB"}
    return querystring


@logger.catch
def stringer(hotels_inf: List, res_dict: Dict, data: Dict) -> Dict:
    """Функция формирования словаря """
    cmd = data['cmd']
    result = res_dict
    for num, hotel in enumerate(hotels_inf, start=len(result) + 1):
        try:
            number_days = calculate_days(arrival_date=data['check_in'], date_departure=data['check_out'])
            current_distance = float(re.search(r'\d\S+', hotel['landmarks'][0]['distance'])[0].replace(',', '.'))
            cost = re.search(r'\d\S+', hotel["ratePlan"]["price"]["current"])[0].replace(',', '')
            current_address = hotel['address'].get('streetAddress')
            if not current_address:
                current_address = 'Точный адрес не указан!'
            if cmd == 'bestdeal':
                if not (data['dist_min'] <= current_distance <= data['dist_max']):
                    continue
            result[num] = dict(
                id=str(hotel['id']),
                name=hotel['name'],
                star_rating=str(hotel["starRating"]).replace(".", ","),
                address=current_address,
                distance=hotel["landmarks"][0]["distance"],
                price_per_night=cost,
                price_per_stay=int(cost) * abs(number_days),
                site=f'https://hotels.com/ho{str(hotel["id"])}'

            )
            if data['pics_amt']:
                result[num]['pics'] = get_pics(hotel['id'], data['pics_amt'])
            if len(result) == data['hotels_amt']:
                break
        except (KeyError, TypeError, ValueError) as exc:
            logger.exception(exc)
            continue

    return result


@logger.catch
def get_pics(hotel_id: str, pics_amt: int) -> List:
    # """pass"""
    resp = None
    pics_list = list()
    url = "https://hotels4.p.rapidapi.com/properties/get-hotel-photos"
    querystring = {'id': hotel_id}
    while not resp:
        resp = request_to_api(url, querystring)
    pattern = r'(?<=,)"hotelImages":.+?(?=,"roomImages)'
    find = re.search(pattern, resp.text)
    if find:
        suggestions = json.loads(f"{{{find[0]}}}")
        for pic in suggestions["hotelImages"]:
            if len(pics_list) == pics_amt:
                break
            pic_url = pic['baseUrl'].replace('_{size}', '')
            if pic_url:
                pics_list.append(pic_url)
    return pics_list
