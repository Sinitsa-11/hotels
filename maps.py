import requests
from data import db_session
from data.places import Place


def find_place(city):
    db_session.global_init("db/hotels.db")
    geocoder_api_server = "http://geocode-maps.yandex.ru/1.x/"

    geocoder_params = {
        "apikey": "40d1649f-0493-4b70-98ba-98533de7710b",
        "geocode": city,
        "format": "json"}

    response = requests.get(geocoder_api_server, params=geocoder_params)

    if not response:
        # обработка ошибочной ситуации
        pass

    # Преобразуем ответ в json-объект
    json_response = response.json()
    # Получаем первый топоним из ответа геокодера.
    toponym = json_response["response"]["GeoObjectCollection"][
        "featureMember"][0]["GeoObject"]
    # Координаты центра топонима:
    toponym_coodrinates = toponym["Point"]["pos"]
    # Долгота и широта:
    toponym_longitude, toponym_lattitude = toponym_coodrinates.split(" ")

    delta = "0.005"

    search_api_server = "https://search-maps.yandex.ru/v1/"
    api_key = "dda3ddba-c9ea-4ead-9010-f43fbc15c6e3"
    toponym_coodrinates = toponym_coodrinates.replace(' ', ',')

    search_params = {
        "apikey": api_key,
        "text": "отель",
        "lang": "ru_RU",
        "ll": toponym_coodrinates,
        "type": "biz",
        "results": "50"
    }

    response = requests.get(search_api_server, params=search_params)
    if not response:
        # ...
        pass

    # Преобразуем ответ в json-объект
    json_response = response.json()

    # Получаем первую найденную организацию.
    organizations = json_response["features"]
    all_hotels = []
    number = 0
    for x in organizations:
        place = Place()
        number += 1
        place.city = city
        place.name = x["properties"]["CompanyMetaData"]["name"]
        place.address = x["properties"]["CompanyMetaData"]["address"]
        if 'url' in x['properties']['CompanyMetaData']:
            place.url = x['properties']['CompanyMetaData']['url']
        else:
            place.url = 'Отсутствует'
        if 'Phones' in x['properties']['CompanyMetaData']:
            phones_lst = []
            phones = x['properties']['CompanyMetaData']['Phones'][0]['formatted']
            phones_lst.append(phones)
            if len(x['properties']['CompanyMetaData']['Phones']) > 1:
                for i in range(1, len(x['properties']['CompanyMetaData']['Phones'])):
                    phones_lst.append(x['properties']['CompanyMetaData']['Phones'][i]['formatted'])
            place.phones = ' '.join(phones_lst)
        else:
            place.phones = 'Отсутствует'
        x_coords = x["properties"]['boundedBy'][1]
        address_ll = ''
        for w in x_coords:
            address_ll += ',' + str(w)
        address_ll = address_ll[1:]
        point = x["geometry"]["coordinates"]
        x_point = "{0},{1}".format(point[0], point[1])
        delta = "0.005"
        map_params = {
            # позиционируем карту центром на наш исходный адрес
            "ll": address_ll,
            "spn": ",".join([delta, delta]),
            "l": "map",
            # добавим точку, чтобы указать найденную аптеку
            "pt": "{0},pm2dgl".format(x_point)
        }
        map_api_server = "http://static-maps.yandex.ru/1.x/"
        # ... и выполняем запрос
        response = requests.get(map_api_server, params=map_params)
        if not response:
            print("Ошибка выполнения запроса:")
            print(map_request)
            print("Http статус:", response.status_code, "(", response.reason, ")")
            sys.exit(1)
        map_file = f"static/maps/{city}_{number}.png"
        with open(map_file, "wb") as file:
            file.write(response.content)
        place.image = map_file
        db_sess = db_session.create_session()
        db_sess.add(place)
        db_sess.commit()


for x in ['Москва', "Санкт-петербург", "Казань", "Екатеринбург", "Сочи", "Калининград", "Ярославль", "Красноярск",
          "Владивосток", "Пятигорск", "Тула", "Южно-сахалинск"]:
    find_place(x)
