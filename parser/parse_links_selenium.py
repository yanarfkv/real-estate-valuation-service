import csv
import json
import os
import locale
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By
from constants import *

locale.setlocale(locale.LC_TIME, 'ru_RU.UTF-8')
driver = webdriver.Chrome()


def save_state(room, object_type, min_price, max_price, page, city_code):
    """
    Сохраняет текущее состояние процесса скрапинга в JSON-файл.
    :param room: Количество комнат.
    :param object_type: Тип объекта (новостройка, вторичное жилье).
    :param min_price: Минимальная цена.
    :param max_price: Максимальная цена.
    :param page: Номер страницы.
    :param city_code: код города
    """
    state = {
        'room': room,
        'object_type': object_type,
        'min_price': min_price,
        'max_price': max_price,
        'page': page,
        'city_code': city_code
    }
    with open(STATE_FILE_LINKS, 'w') as file:
        json.dump(state, file)


def load_state():
    """
    Загружает последнее сохраненное состояние процесса скрапинга из JSON-файла.
    :return: Словарь с состоянием или начальные значения, если файл состояния не существует.
    """
    if os.path.exists(STATE_FILE_LINKS):
        with open(STATE_FILE_LINKS) as file:
            return json.load(file)
    else:
        return {'room': ROOMS[0],
                'object_type': 1,
                'min_price': PRICE_RANGES[0][0],
                'max_price': PRICE_RANGES[0][1],
                'page': 1,
                'city_code': None}


def format_date(date_str):
    """
    Преобразует строку даты в формат 'dd.mm.yyyy'.
    :param date_str: Строка даты публикации.
    :return: Отформатированная дата.
    """
    now = datetime.now()

    if "сегодня" in date_str:
        date = now
    elif "вчера" in date_str:
        date = now - timedelta(days=1)
    else:
        day_month, time = date_str.split(',')
        day, month_str = day_month.split()
        month = datetime.strptime(month_str, "%b").month
        date = datetime(now.year, month, int(day))

    time_str = date_str.split(', ')[1]
    hour, minute = map(int, time_str.split(':'))

    return date.replace(hour=hour, minute=minute, second=0, microsecond=0)


def is_last_page():
    """
    Определяет, является ли текущая страница последней в пагинации сайта.
    :return: True если это последняя страница, иначе False.
    """
    try:
        pagination_div = driver.find_element(By.CLASS_NAME, '_93444fe79c--pagination--UX22n')
        next_span = pagination_div.find_element(By.XPATH, ".//span[text()='Дальше']")
        return next_span.find_element(By.XPATH, '..').tag_name != 'a'
    except NoSuchElementException:
        return True


def write_links(data, city_name):
    """
    Записывает ссылки на объявления и даты их публикации в CSV-файл.
    :param city_name: Наименование города.
    :param data: Словарь с данными о ссылке и дате публикации.
    """
    fieldnames = ['link', 'date']
    links_file_path = f"links/links_{city_name}.csv"
    file_exists = os.path.isfile(links_file_path)

    with open(links_file_path, mode='a', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        writer.writerow(data)


def get_data_page(url):
    """
    Загружает данные со страницы по заданному URL.
    :param url: URL страницы.
    :return: Заголовок страницы или пустая строка при ошибке.
    """
    try:
        driver.get(url)
        return driver.find_element(By.CSS_SELECTOR, 'h1.a10a3f92e9--title--vlZwT').text
    except Exception as e:
        print(f"An error occurred: {e}")
        return ''


def get_page(url, city_name):
    """
    Посещает страницу по указанному URL и извлекает данные о всех объявлениях на этой странице, также определяет,
    является ли эта страница последней в пагинации.
    :param city_name: Наименование города
    :param url: URL веб-страницы для обработки.
    :return: Список словарей, каждый из которых содержит данные одного объявления, и булево значение,
    указывающее на то, является ли страница последней.
    """
    try:
        driver.get(url)

        listings = driver.find_elements(By.CSS_SELECTOR, '._93444fe79c--container--Povoi._93444fe79c--container--Povoi')
        listing_data = []

        for listing in listings:
            link_tag = listing.find_element(By.CLASS_NAME, '_93444fe79c--media--9P6wN')
            date_div = listing.find_element(By.CLASS_NAME, '_93444fe79c--absolute--yut0v')
            if link_tag and date_div:
                date_str = driver.execute_script("return arguments[0].textContent;", date_div)
                date = format_date(date_str)
                link_url = link_tag.get_attribute('href')

                data = {'link': link_url, 'date': date}

                write_links(data, city_name)
                listing_data.append(data)

        return listing_data, is_last_page()

    except Exception as e:
        print(f"An error occurred: {e}")
        return [], True


def create_url(region, room, object_type, page, min_price='', max_price=''):
    """
    Генерирует URL для запроса на основе заданных параметров.
    :param region: Идентификатор региона.
    :param room: Количество комнат.
    :param object_type: Тип объекта недвижимости.
    :param page: Номер страницы для запроса.
    :param min_price: Минимальная цена (необязательный параметр).
    :param max_price: Максимальная цена (необязательный параметр).
    :return: Сформированный URL.
    """
    url_parts = [
        BASE_URL,
        REGION.format(region),
        ROOM.format(room),
        OBJECT_TYPE.format(object_type),
        PAGE.format(page),
        MIN_PRICE.format(min_price) if min_price else '',
        MAX_PRICE.format(max_price) if max_price else ''
    ]
    return ''.join(url_parts)


def extract_links(rooms, price_ranges, cities_list):
    """
    Выполняет процесс извлечения ссылок на объявления по заданным параметрам.
    :param cities_list: Кортеж городов с кодом и наименованием.
    :param rooms: Список количества комнат для поиска.
    :param price_ranges: Список диапазонов цен.
    """
    try:
        state = load_state()
        start_room, start_object_type, start_min_price, start_max_price, start_page, city_code = (
            state['room'], state['object_type'], state['min_price'], state['max_price'], state['page'], state['city_code'])

        city_found = city_code is None

        for city_name, code in cities_list.items():
            if not city_found:
                if code == city_code:
                    city_found = True
                else:
                    continue
            print(f"Обработка города {city_name}")

            for room in rooms[rooms.index(start_room):]:
                print(f"Обработка {room}-комнатных")
                for object_type in range(start_object_type if room == start_room else 1, 3):
                    print(f"Обработка недвижимости типа {object_type}")
                    for min_price, max_price in price_ranges[price_ranges.index((start_min_price,
                                                                                 start_max_price)):] \
                            if object_type == start_object_type and room == start_room else price_ranges:
                        print(f"Обработка недвижимости стоимостью от {min_price} до {max_price}")
                        for page in range(
                                start_page if min_price == start_min_price and max_price == start_max_price
                                              and object_type == start_object_type and room == start_room else 1,
                                55):
                            print(f"Обработка страницы {page}")
                            url = create_url(code, room, object_type, page, min_price, max_price)
                            print(url)
                            listings_data, is_last_page_ = get_page(url, city_name)

                            if not listings_data or is_last_page_:
                                print(f"Ничего не найдено на странице {page}")
                                break

                            save_state(room, object_type, min_price, max_price, page + 1, code)

                        start_page = 1
                    start_min_price, start_max_price = price_ranges[0]
                start_object_type = 1
            start_room = 1

    except KeyboardInterrupt:
        save_state(room, object_type, min_price, max_price, page, code)
        print("Программа прервана пользователем. Состояние сохранено.")
        driver.quit()


if __name__ == '__main__':
    extract_links(ROOMS, PRICE_RANGES, CITIES)
