import requests

#function to first get coordinates of a city and then get its weather
def get_city_weather(city_name):
    geo_url = f'https://geocoding-api.open-meteo.com/v1/search?name={city_name}'

    response = requests.get(geo_url)
        
    geo_data = response.json()['results'][0]
    lat = geo_data['latitude']
    lon = geo_data['longitude']
        
    weather_url = f'https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true&precipitation=true'
        
    weather_response = requests.get(weather_url)
    if weather_response.status_code == 200:
        weather_data = weather_response.json()['current_weather']
        temperature = weather_data['temperature']
        data={
            'temprature':temperature
        }
        return data

#print(get_city_weather('delhi'))
