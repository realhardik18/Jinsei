import requests
import random
import json
import time
import numpy as np
from creds import TOGETHER_API_KEY
import requests
import os

def get_city_weather(city_name):
    geo_url = f'https://geocoding-api.open-meteo.com/v1/search?name={city_name}'

    response = requests.get(geo_url)
    print(response)
        
    geo_data = response.json()['results'][0]
    lat = geo_data['latitude']
    lon = geo_data['longitude']
        
    weather_url = f'https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true&precipitation=true&hourly=relative_humidity_2m'
        
    weather_response = requests.get(weather_url)
    
    if weather_response.status_code == 200:
        weather_data = weather_response.json()['current_weather']
        temperature = weather_data['temperature']
        
        # Get relative humidity from hourly data
        relative_humidity = weather_response.json()['hourly']['relative_humidity_2m'][0]
        
        data = {
            'temperature': temperature,
            'relative_humidity': relative_humidity
        }
        return data
    else:
        return None

#function to get n number of fun facts for a particular plant
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

#function to get a short description about the plant
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

#function to generate all the data and save it into a json file
def generate_textual_data():
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

def initialize_planting_data():
    with open('data/plants.txt','r') as file:
        plants=[plant.strip('\n') for plant in file.readlines()]
        data=dict()
        for plant in plants:
            plant_data=dict()
            plant_data['Trange']=[0,0]
            plant_data['RH']=[0,0]
            data[plant]=plant_data
        with open('planting_data.json','w') as file:
            json.dump(data,file)

#function to retrieve the data
def retrieve_data(plant):
    with open(r'data\textual_data.json','r') as file:
        data=json.load(file)
    return data[plant]        
    
def retrieve_plant_data(plant):
    plant_data=dict()
    plant_data['plant_name']=plant
    plant_data['img']=get_plant_image(plant)
    plant_data['fact']=get_random_fact(plant)
    plant_data['desc']=get_plant_description(plant).replace('**','')
    return plant_data


def get_random_fact(plant):
    return random.choice(list(set(retrieve_data(plant=plant)['facts'])))

def get_plant_description(plant):
    return retrieve_data(plant=plant)['description']
#algorithim which calculates which plant would be the most suited
#first we calculate delta of avg ideal and input temp
#then the same for relative humidity
#then we add the two delta values for overall spread score
#lower the spread score means the plant is more suitable to be planted
def best_match(temp,RH):    
    with open('data\planting_data.json','r') as file:
        data=json.load(file)
    plants=np.array(list(data.keys()))
    deltaTdiff=[abs((sum(data[plant]['Trange'])/2) - temp) for plant in plants]
    deltaRHdiff=[abs(sum(data[plant]['Trange'])/2 - RH)/10 for plant in plants]
    spread_score=np.array([deltaRHdiff[c] + deltaTdiff[c] for c in range(len(plants))])        
    idx=np.argsort(spread_score)
    plants=np.array(plants)[idx]
    spread_score=np.array(spread_score)[idx]    
    return plants[0:3]
    #return plants[0:3]

def get_plant_image(plant_name):
    with open('data/plants.txt','r') as file:
        f=[plant.strip('\n').lower() for plant in file.readlines()]
    return f"{f.index(plant_name)}.png"

    