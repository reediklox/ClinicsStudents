from geopy.distance import geodesic
import urllib.parse
import http.client
import json

class LocationNotFoundError(Exception):
    def __init__(self, *args):
        if args:
            self.message = args[0]
        else:
            self.message = None
            
    def __str__(self) -> str:
        if self.message:
            return f'LocationNotFoundError, {self.message}'
        else:
            return f'LocationNotFoundError, Something wrong with your address!'


class Location:
    def __init__(self, address:str) -> None:
        api_key = 'API_KEY_HERE'
        url = f'/1.x/?format=json&apikey={api_key}&geocode={urllib.parse.quote(address)}'
        connection = http.client.HTTPSConnection('geocode-maps.yandex.ru')
        connection.request('GET', url)
        response = connection.getresponse()
        data = response.read().decode('utf-8')
        connection.close()

        try:
            json_data = json.loads(data)
            coordinates_str = json_data['response']['GeoObjectCollection']['featureMember'][0]['GeoObject']['Point']['pos']
            longitude, latitude = map(float, coordinates_str.split())
            self.point = (latitude, longitude)
        except Exception:
            raise LocationNotFoundError(f"Координаты по адрессу {address} не найдены")
        
    def DistanceDifference(self, location):
        return geodesic(self.point, location.point).kilometers
    