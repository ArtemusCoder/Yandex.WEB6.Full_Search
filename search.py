import sys
from io import BytesIO
import scale_object
import math

import requests
from PIL import Image
import distance

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
    dots = []

    organizations = json_response["features"]
    for organization in organizations:
        org_time = organization['properties']['CompanyMetaData']
        point = organization["geometry"]["coordinates"]
        org_point = "{0},{1}".format(point[0], point[1])
        print(org_time['Hours'])
        if 'Hours' in org_time:
            if 'Availabilities' in org_time['Hours']:
                if 'TwentyFourHours' in org_time['Hours']['Availabilities'][0]:
                    if org_time['Hours']['Availabilities'][0]['TwentyFourHours']:
                        classification = 'pm2rdm'
                    else:
                        classification = 'pm2blm'
                else:
                    classification = 'pm2blm'
            else:
                classification = 'pm2grm'
        else:
            classification = 'pm2grm'
        dot = org_point + ',' + classification
        dots.append(dot)
        delta = "0.005"

    res = '~'.join(dots)

    map_params = {
        "l": "map",
        "pt": "{0}~{1},flag".format(res, coord)
    }

    map_api_server = "http://static-maps.yandex.ru/1.x/"
    response = requests.get(map_api_server, params=map_params)
    Image.open(BytesIO(
        response.content)).show()
