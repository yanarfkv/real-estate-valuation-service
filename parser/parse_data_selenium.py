import csv
import json
import os
import re
from time import sleep
from requests.exceptions import RequestException, ChunkedEncodingError, JSONDecodeError
import requests
from selenium.common import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import osmnx as ox
from osmnx import _errors

from constants import *
from selenium import webdriver

driver = webdriver.Chrome()


def extract_room_count(text):
    """
    Извлекает количество комнат из текста.
    :param text: Текст с описанием квартиры.
    :return: Число комнат (1, 2, 3, ...), 9 для студии, 7 для свободной планировки.
    """
    match = re.search(r'(\d+)-комн.', text)
    if match:
        return int(match.group(1))

    if "студия" in text.lower():
        return 9

    if "свободной планировки" in text.lower():
        return 7

    return None


def extract_coordinates_data(data):
    """
    Извлекает данные координат из полученного словаря данных.
    :param data: Словарь данных, содержащий координаты и адресные элементы.
    :return: Кортеж с координатами и элементами адреса.
    """
    lat = float(data[0]["lat"])
    lon = float(data[0]["lon"])
    city_district = data[0]["address"]["city_district"] if "city_district" in data[0]["address"] else None
    state = data[0]["address"]["state"] if "state" in data[0]["address"] else None
    city = data[0]["address"]["city"] if "city" in data[0]["address"] else None
    road = data[0]["address"]["road"] if "road" in data[0]["address"] else None
    house_number = data[0]["address"]["house_number"] if "house_number" in data[0]["address"] else None

    infrastructure = extract_all_infrastructure(lat, lon)

    return (lat, lon, city_district, state, city, road, house_number, infrastructure['schools'], infrastructure['hospitals'],
            infrastructure['grocery_stores'], infrastructure['kindergartens'])


def extract_all_infrastructure(lat, lon):
    """
    Определяет инфраструктурные объекты вокруг заданной точки.
    :param lat: Широта.
    :param lon: Долгота.
    :return: Словарь с количеством объектов инфраструктуры по категориям.
    """
    tags = {
        'schools': {'amenity': 'school'},
        'hospitals': {'amenity': 'hospital'},
        'grocery_stores': {'shop': ['supermarket']},
        'kindergartens': {'amenity': 'kindergarten'}
    }

    results = {}

    for category, tag in tags.items():
        try:
            geometries = ox.features_from_point((lat, lon), tags=tag, dist=1000)
            results[category] = len(geometries)
        except _errors.InsufficientResponseError:
            results[category] = None

    return results


def process_address(input_string):
    """
    Обрабатывает строку адреса, удаляя ненужные сегменты.
    :param input_string: Исходная строка адреса.
    :return: Очищенная и фильтрованная строка адреса.
    """
    segments = input_string.split(', ')

    cleaned_segments = []
    for segment in segments:
        words = segment.split(' ')
        cleaned_words = [word for word in words if word.lower() not in ["село", "пгт"]]
        cleaned_segment = ' '.join(cleaned_words)
        cleaned_segments.append(cleaned_segment)

    filtered_segments = [segment for segment in cleaned_segments if "респ." not in segment and "р-н" not in segment and "мкр." not in segment]
    result_string = ', '.join(filtered_segments)

    return result_string


def get_coordinates(address, delay=1.1):
    """
    Получает координаты по адресу, используя API OpenStreetMap.
    :param address: Адрес для получения координат.
    :param delay: Задержка между попытками запроса.
    :return: Координаты и связанные данные, если запрос успешен.
    """
    url = f"https://nominatim.openstreetmap.org/search.php?q={address}&format=jsonv2&addressdetails=1&limit=1"

    for _ in range(MAX_RETRIES):
        try:
            response = requests.get(url, headers=HEADERS)
            if response.status_code == 200:
                data = response.json()
                if data:
                    return extract_coordinates_data(data)
            else:
                sleep(delay)
        except JSONDecodeError:
            sleep(delay)
            continue

    return None, None, None, None, None, None, None, None, None, None, None


def get_text_and_lower(element, index):
    """
    Извлекает текст из элемента и приводит его к нижнему регистру.
    :param element: HTML-элемент.
    :param index: Индекс элемента в списке.
    :return: Текст элемента или None, если элемент не найден.
    """
    try:
        ps = element.find_elements(By.TAG_NAME, 'p')
        return ps[index].text.strip().lower()
    except IndexError:
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None


def get_ceiling_height(value):
    """
    Извлекает высоту потолков из строки.
    :param value: Строка с данными о высоте потолков.
    :return: Числовое значение высоты или None при ошибке.
    """
    match = re.search(r"(\d+(?:,\d+)?)", value)
    return parse_float(match.group(1)) if match else None


def get_sum_of_numbers(value):
    """
    Суммирует все числа, найденные в строке.
    :param value: Строка с числами.
    :return: Сумма чисел.
    """
    return sum(map(int, re.findall(r'\d+', value)))


def parse_housing_type(value):
    """
    Определяет тип жилья по заданной строке.
    :param value: Строка с типом жилья.
    :return: Код типа жилья.
    """
    return 1 if value == 'вторичка' else 2


def parse_house_type(value):
    """
    Определяет тип дома по заданной строке.
    :param value: Строка с типом дома.
    :return: Код типа дома или None.
    """
    house_type_mapping = {
        "кирпичный": 1, "деревянный": 2, "монолитный": 3, "панельный": 4, "блочный": 5,
        "кирпично-монолитный": 6, "сталинский": 7
    }
    return house_type_mapping.get(value, None)


def parse_parking(value):
    """
    Определяет тип парковки по заданной строке.
    :param value: Строка с типом парковки.
    :return: Код типа парковки.
    """
    parking_mapping = {"наземная": 1, "подземная": 2, "многоуровневая": 3, "на крыше": 4}
    return parking_mapping.get(value, None)


def parse_repair(value):
    """
    Определяет тип ремонта по заданной строке.
    :param value: Строка с типом ремонта.
    :return: Код типа ремонта.
    """
    repair_mapping = {'дизайнерский': 1, 'евроремонт': 2, 'косметический': 3, 'отсутствует': 4}
    return repair_mapping.get(value, None)


def parse_info_element(element):
    """
    Анализирует HTML-элемент и извлекает информацию по заданной метке.
    :param element: HTML-элемент.
    :return: Ключ и результат парсинга элемента.
    """
    label, value = get_text_and_lower(element, 0), get_text_and_lower(element, 1)
    parse_functions = {
        "тип жилья": ("housing_type", parse_housing_type),
        "общая площадь": ("total_area", parse_float),
        "жилая площадь": ("living_area", parse_float),
        "площадь кухни": ("kitchen_area", parse_float),
        "высота потолков": ("ceiling_height", get_ceiling_height),
        "ремонт": ("repair", parse_repair),
        "год постройки": ("house_year", lambda v: v),
        "тип дома": ("house_type", parse_house_type),
        "вид из окон": ("windows_view", lambda v: 1 if v == "во двор" else 2 if v == "на улицу" else None),
        "санузел": ("bathrooms_num", get_sum_of_numbers),
        "парковка": ("parking", parse_parking),
        "количество лифтов": ("elevators_num", get_sum_of_numbers),
        "балкон/лоджия": ("balcony_num", get_sum_of_numbers)
    }
    if label in parse_functions:
        key, parse_function = parse_functions[label]
        return key, parse_function(value)

    return None, None


def parse_float(value):
    """
    Преобразует строку в число с плавающей точкой, заменяя запятые на точки.
    :param value: Строка с числовым значением.
    :return: Число с плавающей точкой или None при ошибке.
    """
    try:
        return float(value.replace(',', '.'))
    except ValueError:
        return None


def get_full_address(driver):
    """
    Извлекает полный адрес из элементов на веб-странице.
    :param driver: Веб-драйвер для доступа к элементам страницы.
    :return: Строка с полным адресом.
    """
    try:
        address_elements = driver.find_elements(By.CSS_SELECTOR, 'a.a10a3f92e9--address--SMU25')
        return ', '.join([element.text for element in address_elements])
    except Exception as e:
        print(f"An error occurred while getting the full address: {e}")
        return ''


def check_floor_icon_exists(block):
    """
    Проверяет наличие иконки этажа в блоке информации.
    :param block: HTML-блок для проверки.
    :return: True, если иконка найдена, иначе False.
    """
    try:
        floor_icon = block.find_element(By.CSS_SELECTOR, "img[src*='floor.svg']")
        return floor_icon is not None
    except Exception as e:
        print(f"An error occurred floor: {e}")
        return False


def get_page(url):
    """
    Получает данные со страницы по указанному URL.
    :param url: URL веб-страницы.
    :return: Словарь с распарсенными данными.
    """
    try:
        driver.get(url)

        try:
            price_element = driver.find_element(By.CSS_SELECTOR, '.a10a3f92e9--input--YmTjn').get_attribute('value')
            normalized_string = price_element.replace('\u2009', '')
            price = int(normalized_string)
        except Exception as e:
            price_element = WebDriverWait(driver, 5).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, '.a10a3f92e9--amount--ON6i1 span'))
            )
            price = price_element.text
            price = price.replace(' ', '').replace('₽', '')

        title = driver.find_element(By.CSS_SELECTOR, 'h1.a10a3f92e9--title--vlZwT').text
        rooms = extract_room_count(title)

        full_address = get_full_address(driver)
        (latitude, longitude, city_district, state, city, road, house_number, schools, hospitals, grocery_stores,
         kindergartens) = get_coordinates(process_address(full_address))

        floor, total_floors = None, None

        blocks = driver.find_elements(By.CSS_SELECTOR, 'div.a10a3f92e9--item--Jp5Qv')
        for block in blocks:
            if block.find_elements(By.CSS_SELECTOR, "img[src*='floor.svg']"):
                floor_info = block.find_element(By.CSS_SELECTOR, 'span.a10a3f92e9--color_black_100--Ephi7').text
                try:
                    floor, total_floors = floor_info.split(' из ')
                except ValueError:
                    floor, total_floors = None, None

        parsed_data = {
            'price': price,
            "rooms": rooms,
            'full_address': full_address,
            'latitude': latitude,
            'longitude': longitude,
            'city_district': city_district,
            'state': state,
            'city': city,
            'road': road,
            'house_number': house_number,
            'floor': floor,
            'total_floors': total_floors,
            "housing_type": None,
            "total_area": None,
            "living_area": None,
            "kitchen_area": None,
            "ceiling_height": None,
            "repair": None,
            "house_year": None,
            "house_type": None,
            "windows_view": None,
            "bathrooms_num": None,
            "parking": None,
            "elevators_num": None,
            "balcony_num": None,
            "schools": schools,
            "hospitals": hospitals,
            "grocery_stores": grocery_stores,
            "kindergartens": kindergartens
        }

        info_elements = driver.find_elements(By.CSS_SELECTOR, '.a10a3f92e9--item--qJhdR')
        for element in info_elements:
            key, result = parse_info_element(element)
            if key:
                parsed_data[key] = result

        return parsed_data

    except (ChunkedEncodingError, RequestException, TimeoutException, Exception) as e:
        print(f"Ошибка: {e}")

    return {}


def save_state(city, index):
    """
    Сохраняет текущее состояние парсера в JSON-файл.
    :param city: Название города.
    :param index: Индекс последней обработанной строки.
    """
    with open('data/state_data.json', 'w') as file:
        json.dump({"last_city": city, "last_index": index}, file)


def load_state():
    """
    Загружает последнее сохраненное состояние парсера из JSON-файла.
    :return: Кортеж с названием города и индексом последней обработанной строки.
    """
    if os.path.exists('data/state_data.json'):
        with open('data/state_data.json') as file:
            state = json.load(file)
            return state.get("last_city", None), state.get("last_index", 0)
    return None, 0


def run_parse_data():
    """
    Основная функция для запуска парсера данных для определенного города.
    """
    try:
        last_city, last_index = load_state()
        cities_list = list(CITIES.keys())

        # Определение начального города
        start_index = cities_list.index(last_city) if last_city in cities_list else 0

        for city in cities_list[start_index:]:
            links_file = f'links/links_{city}.csv'
            data_file = f'data/data_{city}.csv'

            try:
                with open(links_file, newline='') as csvfile_in, open(data_file, mode='a', newline='') as csvfile_out:
                    reader = csv.DictReader(csvfile_in)
                    fieldnames = [
                        'link', 'date', 'price', 'rooms', 'full_address', 'latitude', 'longitude', 'city_district',
                        'state', 'city', 'road', 'house_number', 'floor', 'total_floors', 'housing_type',
                        'total_area', 'living_area', 'kitchen_area', 'ceiling_height', 'repair', 'house_year',
                        'house_type', 'windows_view', 'bathrooms_num', 'parking', 'elevators_num', 'balcony_num',
                        'schools', 'hospitals', 'grocery_stores', 'kindergartens'
                    ]
                    writer = csv.DictWriter(csvfile_out, fieldnames=fieldnames)

                    if last_index == 0 or city != last_city:
                        writer.writeheader()

                    for i, row in enumerate(reader, start=1):
                        if city == last_city and i <= last_index:
                            continue

                        parsed_data = get_page(row['link'])
                        if parsed_data:
                            row_data = {'link': row['link'], 'date': row['date'], **parsed_data}
                            writer.writerow(row_data)
                            save_state(city, i)

            except FileNotFoundError:
                print(f"Файл {links_file} не найден.")
    except KeyboardInterrupt:
        print("Программа прервана пользователем. Состояние сохранено.")
        driver.quit()


if __name__ == "__main__":
    run_parse_data()
