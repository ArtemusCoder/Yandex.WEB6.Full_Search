import sys
from io import BytesIO
import scale_object
import math

import requests
from PIL import Image
import distance

import math

snippet = {'Расстояние: ': None, 'Адрес аптеки: ': None, 'Название аптеки: ': None, 'Время работы: ' : None}

toponym_to_find = " ".join(sys.argv[1:])

search_api_server = "https://search-maps.yandex.ru/v1/"
api_key = "..."

geocoder_api_server = "http://geocode-maps.yandex.ru/1.x/"

geocoder_params = {
    "apikey": "40d1649f-0493-4b70-98ba-98533de7710b",
    "geocode": toponym_to_find,
    "format": "json"}

response = requests.get(geocoder_api_server, params=geocoder_params)

if not response:
    print('Not response')
else:
    json_response = response.json()
    toponym = json_response["response"]["GeoObjectCollection"][
        "featureMember"][0]["GeoObject"]
    toponym_coodrinates = toponym["Point"]["pos"]
    coord = toponym_coodrinates.replace(' ', ',')
    toponym_longitude, toponym_lattitude = toponym_coodrinates.split(" ")
    toponym_coodrinates = toponym_coodrinates.split()
    toponym_envelope = toponym['boundedBy']['Envelope']
    lower_corner = toponym_envelope['lowerCorner'].split()
    upper_corner = toponym_envelope['upperCorner'].split()

    scale = scale_object.scale(lower_corner, upper_corner)

search_params = {
    "apikey": '9431a5a3-2f22-493d-81f4-65093e01ba58',
    "text": "аптека",
    "lang": "ru_RU",
    "ll": coord,
    "type": "biz"
}

response = requests.get(search_api_server, params=search_params)
if not response:
    print('WRONG')
else:
    json_response = response.json()

    # Получаем первую найденную организацию.
    organization = json_response["features"][0]
    # Название организации.
    org_name = organization["properties"]["CompanyMetaData"]["name"]
    # Адрес организации.
    org_address = organization["properties"]["CompanyMetaData"]["address"]
    org_time = organization['properties']['CompanyMetaData']['Hours']['text']

    snippet['Адрес аптеки: '] = org_name
    snippet['Название аптеки: '] = org_address
    snippet['Время работы: '] = org_time

    # Получаем координаты ответа.
    point = organization["geometry"]["coordinates"]
    org_point = "{0},{1}".format(point[0], point[1])
    delta = "0.005"

    # Собираем параметры для запроса к StaticMapsAPI:
    map_params = {
        "l": "map",
        "pt": "{0},pm2dgl~{1},flag".format(org_point, coord)
    }

    map_api_server = "http://static-maps.yandex.ru/1.x/"
    response = requests.get(map_api_server, params=map_params)
    Image.open(BytesIO(
        response.content)).show()

a = [float(i) for i in point]
b = [float(i) for i in toponym_coodrinates]

snippet['Расстояние: '] = str(int(distance.lonlat_distance(a, b))) + ' метров'
for key, value in snippet.items():
    print(key, value)
