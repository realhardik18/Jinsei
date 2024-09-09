import requests
import json
import time
from creds import TOGETHER_API_KEY

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

def fun_fact_generator(plant_name):
    prompt=f'give me a short fun fact about the plant "{plant_name}"'
    url = "https://api.together.xyz/v1/chat/completions" 
    headers = {
        "Authorization": f"Bearer {TOGETHER_API_KEY}",  
        "Content-Type": "application/json"
    }
    data = {
        "model": "meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo",
        "messages": [{"role": "user", "content": prompt}]
    }

    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 200:
        completion = response.json()
        return completion['choices'][0]['message']['content']
    else:
        print(f"Error: {response.status_code}, {response.text}")
        return None

def description_generator(plant_name):
    prompt=f'give me a short description about the plant "{plant_name}"'
    url = "https://api.together.xyz/v1/chat/completions" 
    headers = {
        "Authorization": f"Bearer {TOGETHER_API_KEY}",  
        "Content-Type": "application/json"
    }
    data = {
        "model": "meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo",
        "messages": [{"role": "user", "content": prompt}]
    }

    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 200:
        completion = response.json()
        return completion['choices'][0]['message']['content']
    else:
        print(f"Error: {response.status_code}, {response.text}")
        return None


def generate_data():
    with open('plants.txt','r') as file:
        plants=[plant.strip('\n') for plant in file.readlines()]

    DataBase=dict()

    for plant in plants:
        print(f'generating data for {plant}...')
        plant_data=dict()
        facts=list()

        for _ in range(5):
            print(f'generating fact-{_}...')
            facts.append(fun_fact_generator(plant))
            time.sleep(10)

        plant_data['facts']=facts
        plant_data['description']=description_generator(plant)
        DataBase[plant]=plant_data
        print(f'done generating data for {plant}')
    with open('db.json','w') as file:
        json.dump(DataBase,file)

def retrieve_data():
    with open('db.json','r') as file:
        data=json.load(file)
    for plant in list(data.keys()):
        print(data[plant]['description']!=None)



#retrieve_data()
generate_data()
