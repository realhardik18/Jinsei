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
    plant_data['amazon_link']=get_link(plant)
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

def get_link(plant_name):    
    links=['https://www.amazon.in/Gifti-Variety-Chinese-Abutilon-hibiscus/dp/B0CXSLBXMV/ref=sr_1_1_sspa?crid=551W827CTIM8&dib=eyJ2IjoiMSJ9.O92utmzqi75l66LWRDecOwvuVyNTPlVYIquWQKfpdi7vmlsrVyvVsdv6OrEXJD3LtUkd0XHSJr53Et3GZM5QL7QmibD7g38H7TcufPiBnNnXlWFWJzk4UJcWvA42TQVme9eBsukpjzKfZeAPTl9cgD1Zhib7LDQfAEvom24sIUOD5yhBeD4SOeiEnl-CwrOXYezZRrliFcMLcbIEDq4dX1kzHTZ5InHNLc07z3HvsSDYvZ69jA-DJKcENXSEwLE7KjdjrQ5_UGu9-8ePuXcjedhnRjV8Qkt2O05KcMqGJ5Y.5M5ZtKhAO44l6CUOUuKbAzFwtE3Gl2k7gEsRHxEkcWE&dib_tag=se&keywords=chinese+hibiscus+plant&qid=1725941942&sprefix=chinese+hibiscus%2Caps%2C321&sr=8-1-spons&sp_csd=d2lkZ2V0TmFtZT1zcF9hdGY&psc=1',
           'https://www.amazon.in/sspa/click?ie=UTF8&spc=MTozMjgyNzIyMjAyNjEzMDk0OjE3MjU5NDE5ODA6c3BfYXRmOjMwMDMxODI5NjAyODAzMjo6MDo6&url=%2FFlorona-pepper-PANNIYUR-peppercorn-Healthy%2Fdp%2FB09HHHX2NS%2Fref%3Dsr_1_2_sspa%3Fcrid%3D2NLVMCEWAHI9R%26dib%3DeyJ2IjoiMSJ9.xI3QSbdsBI_M31mZpZToh_r6jcMvGwKr7RAQfc2C6JgeMyagbh-XJnysldhgKgyEErvSoRFaJAIiSMVJWYAvv-Ih3K1YZ9zqwlLYthLdiVObV-BEdBkI-9H6uLC8vWov4R0u3q56YLj-61BFY_VslXiilSqWO4W9bpYuL3FAKjjsO6XYhpCAQ0CBYnQCpAD24HITCj-cbhRtajIJKEJ43GhjHOocIbFDHOKQTWi3jXMgyouDkqvCRkgIqIDYmU8I4IMfHnzLmQqeocP--_iiimHgLwbn3hnpCqRUpMH5A60.KIxJe_4WLBL_WbnpmTksZJpqwip4-ly3lmOMfEGBNhQ%26dib_tag%3Dse%26keywords%3Dpepper%2Bplant%26qid%3D1725941980%26sprefix%3Dpeppperpla%252Caps%252C395%26sr%3D8-2-spons%26sp_csd%3Dd2lkZ2V0TmFtZT1zcF9hdGY%26psc%3D1',
           'https://www.amazon.in/sspa/click?ie=UTF8&spc=MTo1MzU5NjcxNDAxNTI5NTY0OjE3MjU5NDIwMDQ6c3BfYXRmOjMwMDMyNTg1NTE3MTkzMjo6MDo6&url=%2FRukonza-Shami-Plant-Vanni-Maram%2Fdp%2FB0D4WNZ8K6%2Fref%3Dsr_1_1_sspa%3Fcrid%3DGO9SGL92953M%26dib%3DeyJ2IjoiMSJ9._c8YWoge58ecZaWGN6SjoogNjyb4REWKdT_J90j8RSLgrMHds53QIFXPf2uX0V6zogHQXR3FFd5PNGyNHmyInHr2ia8egoCFPZTrfXQQA7e3V3z6tIf5FZQ9QDMLu53qNiQzYCiKqcWnAsQTB6mXX3qPqde_iNHK9156Bw7V9WqPhHaxgjM3Ya9pMEWQH6e3kv91SSUS2qKADLeOuvnJkRMkbf44dZyy4jOs1iLmmzYGxO4iW25J6kuDPHL9t_RMSmZqYx75x-8iQ2hfaTr14V5WNZ03CO4D5Is-WBjIs1c.7J20IYQT5T9xMOZGHmM2c1DURyKJe_P1iEtigmCfW9k%26dib_tag%3Dse%26keywords%3Doleander%2Bplant%26qid%3D1725942004%26sprefix%3Doleander%2Bpla%252Caps%252C222%26sr%3D8-1-spons%26sp_csd%3Dd2lkZ2V0TmFtZT1zcF9hdGY%26psc%3D1',
           'https://www.amazon.in/sspa/click?ie=UTF8&spc=MTo0MTM2MDg0ODQwMTE1MTQ0OjE3MjU5NDIwMjI6c3BfYXRmOjMwMDA2MTc4NjQ2NjEzMjo6MDo6&url=%2FCreative-Farmer-Madagascar-Periwinkle-Kitchen%2Fdp%2FB078R65YSF%2Fref%3Dsr_1_1_sspa%3Fcrid%3D1V0DWYCZ4PBD9%26dib%3DeyJ2IjoiMSJ9.WahLkl08hhNIwu7_YiltSXqjdmzJA6Jr84YAGSh_qI8PdrYcrotKC-bN3ireCWrt5_7MajGylAyTDxEJUDLPRpYCQm6RIA1xNigRgGFBQvPEs_D7m-VgLX13vrfGUc3JwV7mmLYBmlaNI74CFlyd8QZgvnkol4M3Y4kidkOUCl9CI0GoLNfcZO3BKZK6HZFSslAAGQZWK56iDYck6F3HBmDKBt4ZJne8KB4jep5jl9FpWBuyRuvlKsWJomGBzFWzt_Pc6EDFw3eqqBfkjFgLVbvl6BKuO_ESFbHlxG3GhPM.NKIVwxFOmCrCdKzK9t48ZX9QchFZcFwebxl-0776dF0%26dib_tag%3Dse%26keywords%3DMadagascar%2Bperiwinkle%26qid%3D1725942021%26sprefix%3Doleander%2Bplant%252Caps%252C267%26sr%3D8-1-spons%26sp_csd%3Dd2lkZ2V0TmFtZT1zcF9hdGY%26psc%3D1',
           'https://www.amazon.in/little-jungle-Golden-pothos-Nursery/dp/B094CW4K9K/ref=sr_1_5_mod_primary_new?crid=1J54R2A5IGZ48&dib=eyJ2IjoiMSJ9.t-Qzb3vZDSLstO4sfqllT-cci7UJ3brcsd7HGESw71lougnY0FTntEmmIXzZrHpLiRy5EDODwMr2ZDhsTtdTiAFrbN0OXTg47FarzRW6W-TQL2_ahF7Wk0RV0TskdFVJcUbpkY8Op7wz3-Pi1QECGiquPbyojRvVbsSEf17IhEBQWx2X4--FDN_P5ENtxJbL7Qp04XgvOzXo0kGfjtdf2NIi3ukinAwJwhDLabP_35onEtcjOAE05WCl7HdFqQVzqHxNG00XBBGy9m9m_hJSYbjIRFi17UW4nIg5PkA_dGA.kaL91F1GE0icXNymHZsav7Vv0hCCzG2HSN3GAsDTCeM&dib_tag=se&keywords=golden+pothos+plant&qid=1725942043&sbo=RZvfv%2F%2FHxDF%2BO5021pAnSA%3D%3D&sprefix=golden+photos+p%2Caps%2C423&sr=8-5',
           'https://www.amazon.in/Mphmi-Plant-Ixora-Any-Color/dp/B08VHF3XKW/ref=sr_1_1_sspa?crid=1XPWJ9JKWU6QM&dib=eyJ2IjoiMSJ9.ud6dXMwXhsAvqptXBNJr-dIO6KGhdogv0zsBQnWRF6ToazcDSTrAhz1jv6b8gRs8Bh0hyFXBePKbCXlxAa5bP6o0yKuZRi2iRhSN48DqVMPpSQEqOAt7lq1kAn5X8NRE5q23MJhwckpTJRGcJwnkUyKxgKfTRq40yu31kSXSnUdy0J1gQ-1E3JtSeznPSk7-N2ornbrwSGdb8Q1zm5Fywwlr-E2iXhoDz8rrPhENgoDec3vpi7mPPoOG7iUeQrS9fVWRTSDUAQthRuIRBbbQ3BoAgfFG88IGfUTBA3O5WlA.LvswU6jSOewOsjrBQeQjyWqJzjd8Xw_Z5Db7YH5KvFg&dib_tag=se&keywords=flame+of+the+woods+plant&qid=1725942066&sprefix=flame+of+the+wods+p%2Caps%2C417&sr=8-1-spons&sp_csd=d2lkZ2V0TmFtZT1zcF9hdGY&psc=1',
           'https://www.amazon.in/Garden-Art-Aloe-Vera-Succulent/dp/B09TDTD2CD/ref=sr_1_4_sspa?crid=TVZJB24NLCMK&dib=eyJ2IjoiMSJ9.tKaZhwT4L8mEBzMb4TjhNvmAKhH4Equ-FAC7syPv0_uaImLiPojXsAm9Trt5k35RuA7SmIZMtYeLCmSiuXDaALEfs2oFua6j-GCAxLtPkB9Vtfk3PyqCUnyQdYSO59CaZmGFg39j4cpDUPtXt3k1sdlehq4ePsC78DWDcEStJPG46WiHtpRa1eHqTR8n8Qc6hI3glM3vO9nxHCyEomcvET9IFCDl8Lp1sBRnCXm505P9jfnPHHOGwXF5fV16Etjw41i2_5A2_knnSeDmCZeDGbrZNdxYL1MsLQ_9ZUsfGj4.jdtedNOhvmpVDlXs2pCp_onofQ6YFFKVS3WQXiUWBSA&dib_tag=se&keywords=aloe+vera+plants&qid=1725942082&sprefix=aloe+vera+plan%2Caps%2C236&sr=8-4-spons&sp_csd=d2lkZ2V0TmFtZT1zcF9hdGY&psc=1',
           'https://www.amazon.in/Cypress-Portulaca-Oleracea-purslane-cuttings/dp/B0BMGV79M4/ref=sr_1_1_sspa?crid=39LJ8QCZQ9SE8&dib=eyJ2IjoiMSJ9.Gb0aCIDjfJP4Q0UGH9lC3rU_812H90p3H8T0-DBtVvJeGreVwsF-bRbBBJVvBL0edx5H4rt9EgYrto6JT6PIpb0ix-0npZJihWIbPnd0oxPm4Um9Ca3lGyX3l78LExZekIOLwuMc2xbuB0VVvgtvJTVUxFeDL5ik0HKiFHRv8IJ4Ekm2UKTpz60mgubwld-mkVuYgW50tziI_nX6KOJ9uyBR2e2I3H1UeAen1yNBfZ3RKx38cpizl40s_NpFsvLS9gBRe_ARkXhOt2TXDRGUaVuRxqNLS1vBD7ded_8SBus.ZEzuKCZuaokMAE2oESrqXZmYcg7cvf0QVyAYmFj9raE&dib_tag=se&keywords=Common+purslane+plants&qid=1725942098&sprefix=common+purslane+pla%2Caps%2C304&sr=8-1-spons&sp_csd=d2lkZ2V0TmFtZT1zcF9hdGY&psc=1',
           'https://www.amazon.in/EverSneh-Euphorbia-Plant-Flowers-Healthy/dp/B0B45SSCW6/ref=sr_1_2?crid=XTPHZ72SQ74K&dib=eyJ2IjoiMSJ9.i7BnAJAJvFK8xasObN01wEP6__mAIxAsTm0FOLAFiQFEQoVTtNyBPkdpt3qwX_1s07N-oscK7djsTXqz-upzInfSXoH9-5BP2LThG6Xk25WXnu8A8wrvHdmY6crRiPP2q7u8eY34WAT5Nx3eDYvEZcSslOaGZA9vC465ma_aFZ7W3baPjQKNXUnuK2IFPsWiLjBsIBvBB3lxtZgEwA3JL7JicEawLu6qmoCj0kyvhMQ_AOVpuCf-IADhxZ3UdVUUNGY3bC2ueCT252FuXpp9rVYfLGE-HpsR6Yx99QIbF3c.Ick_A_337_ORLsYQFYzZmDvzw6NOLUCmYOV-aQE0jpo&dib_tag=se&keywords=Crown+of+thorns&qid=1725942117&sprefix=crown+of+thorns%2Caps%2C280&sr=8-2',
           'https://www.amazon.in/sspa/click?ie=UTF8&spc=MToxMjk1Nzk3NTY2NDkzMTA4OjE3MjU5NDIxMzI6c3BfYXRmOjMwMDE1NjcxNDA3MDgzMjo6MDo6&url=%2FHug-Plant-Watermelon-Peperomia-argyreia%2Fdp%2FB0C6G9LPWX%2Fref%3Dsr_1_3_sspa%3Fcrid%3D6IWHMMKM8XL8%26dib%3DeyJ2IjoiMSJ9.i-xjMarokzQ48IAISb1ZO2rBHOvGPzbaGCRmKRla58Zhql5QIEbq8Gz2am1zb53o4anz4TShfCTTphiHccWOvVL5tr3W_5CmgZMvWUyKdv3IGBR-DyGapYGUIXLvJxDzY0v75MXKGMOrhkOkbcxolm-mbOsxvEtDPTurSTjeBCquO5p1anXjn8qFvBzQs15YGNgcQ9ebZvnt_fvUkc2yCtMxaOeO0zaobMJqBb224mrDxFmT-UPzWjNncxAVKAYULk4KZGKHPkzlqcjU2HGf0aubzlSisoI-LIOZVGERE8E.3ZIc6V9BPjZXzdJISm8SDsCqQGrFEsQwnTs_S7CZnD0%26dib_tag%3Dse%26keywords%3Dwatermelon%2Bplant%26qid%3D1725942132%26sprefix%3Dwatermelon%2Bpla%252Caps%252C242%26sr%3D8-3-spons%26sp_csd%3Dd2lkZ2V0TmFtZT1zcF9hdGY%26psc%3D1',
           'https://www.amazon.in/PlantaZee-Live-Tomato-Tamatar-Plant/dp/B0B1V1DM4L/ref=sr_1_9?crid=1ATLFONFDANIT&dib=eyJ2IjoiMSJ9.4jQqFfEY-P7OaiyPkQOYEO-OOHnIr6OhQWeNnrXdnZS4E6NLk8-P41f64KExTO-GennQRYanoWK3bPjbHONiDQe5qpm5YYnka97fGJr2kz3XNI-BSNp3-DgQkFok8BkZpbYAXNu8x_vlpv45ZvVc0uoBvQgTcawWUauA_fgmL2smZvdwqFPOqCsZ4AkBewI_KWndyrHAgyJ7e8rmshoTLIynyYlc8abAxI63x2iyWBGbs-43_InFyfYIvpME8VLdZsyTfU76AmMvoMsu2s28ELHfhiaZ7LcOMtLktjatsvY.QVVQSMtsvIdlJAtvEObryVd_SUWGYWwTnFykNX_HZ2I&dib_tag=se&keywords=tomato+plant&qid=1725942519&s=garden&sprefix=tomato+p%2Clawngarden%2C219&sr=1-9',
           'https://www.amazon.in/sspa/click?ie=UTF8&spc=MToyNjQ1ODQ2MjAzMTQ3MDoxNzI1OTQyMTk4OnNwX2F0ZjozMDAxNzk4NzcyMzgwMzI6OjA6Og&url=%2FDaymond-Gouva-Plant-Layering-Fruiting%2Fdp%2FB0D3F83SZ6%2Fref%3Dsr_1_1_sspa%3Fcrid%3D2LEUJELWFE45D%26dib%3DeyJ2IjoiMSJ9.5NeLaCEugce8MqAxOjrt9qygX753M3Z6LeWUfLKnwCoNOKRxxg5Br0YSeIkp1NXFKVwNPZCkMG9bgpLCyhbUznpH5NUHfiIpLJpMadtccGABYNQghf5jpiSp5UicOqFzt8lP7ZqG3h1RwImpxl3yrXLfD1gt22RK99XNesBPbYAGhA7SQlifM2aw9pNRydNZ_3SaZkucWh_kUcEEa5OJFzCsL1QQBaDl-pdxSitNehZ6jtYnnyLnnICJoDD6IptA9I8T-e14_IclMS58PyvuwH7e87FXOPcvLy4cv2wp1Ok.zNzGycPdZ25obnm8gG3eweraaUOKOVSJGllj43PTA5w%26dib_tag%3Dse%26keywords%3DGuava%2Bplants%26qid%3D1725942198%26sprefix%3Dguava%2Bplants%252Caps%252C264%26sr%3D8-1-spons%26sp_csd%3Dd2lkZ2V0TmFtZT1zcF9hdGY%26psc%3D1',
           'https://www.amazon.in/sspa/click?ie=UTF8&spc=MToyMTExMDE4OTM2MTg5MTM2OjE3MjU5NDIyMzc6c3BfYXRmOjIwMDg2NDYyNzMyMDk4OjowOjo&url=%2FUgaoo-Croton-Petra-Self-Watering%2Fdp%2FB07QXSKK5Y%2Fref%3Dsr_1_1_sspa%3Fcrid%3D23JH9G29CHTUO%26dib%3DeyJ2IjoiMSJ9.fMontcnTsfWvdIn98UsZbedD66UoP0XLPqZz7qRqYxzD35x0KqEraCA1wlRGfH0KBrJS1m0D4PsTMjeK87fXhQ5SKB9caPtSa8A6RJPm-ou67lW9OYg937vr6RCHV2Q9N1fYpxZ6W8dpJcK_3dlxH4SEo5w6fHTrqJZxUG6KhlMXhQDqk_aCeaevrpxKZE8zYVLd3izy-6S9bzcZCNMw0eRRTRdCmDPV5jUsEiBPAAdr4-rjU79EkECbwMZAavaW9-KVB17MmDjYKdmr5Xhq4thl77cGf4LktEcPlxsCf6I.KfGvqkA7zlvs2aF0B6_-Hm9AUHuxykYrQrEDqSDGKc0%26dib_tag%3Dse%26keywords%3Dgarden%2Bcroton%2Bplant%26qid%3D1725942237%26sprefix%3Dgolden%2Bcotton%2Bpla%252Caps%252C237%26sr%3D8-1-spons%26sp_csd%3Dd2lkZ2V0TmFtZT1zcF9hdGY%26psc%3D1',
           'https://www.amazon.in/sspa/click?ie=UTF8&spc=MToxNzMyODA5MDQwNTQ0NzYxOjE3MjU5NDIyMTg6c3BfYXRmOjMwMDEzMjY4NDYxMjIzMjo6MDo6&url=%2FKalfo-Shyama-Tulsi-Ayurvedic-Plants%2Fdp%2FB0CVH6QGW8%2Fref%3Dsr_1_1_sspa%3Fcrid%3D3C6OWAUJS2AWR%26dib%3DeyJ2IjoiMSJ9.-dV_DhvIkU1eWNlClFMd0ZyUqwfz2EkSB3fPQdhdK4AuAvKmfK9fWuv81aMZGh50O-uUcxoPjv5iH4oLR7oZJ5gyt9MpaIDg-00OvNG7vjXru_5Mzdq3FSjqE3novEAAo0vCkDJAERLCUy62kSSR3GMBxLEsOgAM68QsYYHwFOJvBpmAXg0R8JGeZkEs3YNPjeKBbrvyhCJNBjAMIdxuPSiiiTJh9kmw7_heUgRXsPzEvIvFO07r7sZzZe0bG50t8LFSVrQ_5zurqC2OtT3FWUiVnKzE5VbsoLHvk1FEP80.kF84xZHd5AgIbujBMgzd1FQco-C0daiAWNOoRx8klKw%26dib_tag%3Dse%26keywords%3Dholy%2Bbasil%2Bplant%26qid%3D1725942217%26sprefix%3Dholy%2Bbasil%2Bp%252Caps%252C234%26sr%3D8-1-spons%26sp_csd%3Dd2lkZ2V0TmFtZT1zcF9hdGY%26psc%3D1',
           'https://www.amazon.in/sspa/click?ie=UTF8&spc=MTo1NjA5MjcxNzMxNzA1ODQxOjE3MjU5NDIzMDQ6c3BfYXRmOjIwMDg1MTA0MTg0OTk4OjowOjo&url=%2FPlantzoin-Fancy-Leaf-Caladium-Heart-bicolor%2Fdp%2FB093DVHCSH%2Fref%3Dsr_1_1_sspa%3Fcrid%3D32YWFGHOMT2CG%26dib%3DeyJ2IjoiMSJ9.jVW_7Hf0_F3NDH_CXiH8tY9VT59D69sRUbwJCd0dILfn1VJSGxdcXv3l3Qb7fKFbAxYVW-ZEG8LxQWOdyDBwXpDuTsIajCsJFugqlQLrQMYMkuzOYT0aB1FoWuwcMgL2QPE9jvjUjpEfLPFQKJymx_1ZYUR09DoSQFb3OVgnd4-xoqZvtmMARguAhPdpscmkY-M2dhIcwBBrhxpmwR8nxwM4MW9PQNMOwXSrZvmjCb3xSGnjzXrh-61RgkGTN-ouZmzzSbFuSgA8e8ap1TelaJUo0xjvQYhat4vFrdwApFY.Ua5AtKOE5ZWFFl6xhc7jaNT9HPVKjPedwwVWFggp2-w%26dib_tag%3Dse%26keywords%3DHeart%2Bof%2Bjesus%2Bplant%26qid%3D1725942303%26sprefix%3Dheart%2Bof%2Bjesus%2Bplant%252Caps%252C272%26sr%3D8-1-spons%26sp_csd%3Dd2lkZ2V0TmFtZT1zcF9hdGY%26psc%3D1',
           'https://www.amazon.in/sspa/click?ie=UTF8&spc=MToyMTI1OTM4NjE0NTUyNjcyOjE3MjU5NDIzMjQ6c3BfYXRmOjMwMDMyMDk3NjIwMzIzMjo6MDo6&url=%2FMphmi-Nursery-Caesalpinia-Pulcherrima-Paradise%2Fdp%2FB0BV2VYHNG%2Fref%3Dsr_1_1_sspa%3Fcrid%3D231E5N1BZUAD5%26dib%3DeyJ2IjoiMSJ9.OTsiv4ZMuyMMeI-YOtpzUWF_EY9343SPrgXd2wLK4FwzbMb2fkIi9R8tua8RyAoXj1MjHqaCYG3RzHSt2zaDvPPjj54j6EEyoP-vUXHUYNTSei3RgldZClb2j659M40AnMl49tv6ggJxOJAwpPx4p01MieDUXLquWtG6dtt3Hqm_fQRiQElf_yphJuu5wyYz1lr3tpHEYQ0QzptrdyVLKtWa5PpOX9nqbOXfENx9mIody6LBocSEJ4sg4gFu2deL6CC_pPpTKpzqdKdCSLgjElTrdIq4nvDXrM6dLTv20As.mxwiP3E17VQUqKanGix6nRXZWtHekOWdlIWjg0w7OfY%26dib_tag%3Dse%26keywords%3DPeacock%2Bflower%2Bplant%26qid%3D1725942323%26sprefix%3Dpeacock%2Bflowerplant%252Caps%252C257%26sr%3D8-1-spons%26sp_csd%3Dd2lkZ2V0TmFtZT1zcF9hdGY%26psc%3D1',
           'https://www.amazon.in/sspa/click?ie=UTF8&spc=MTo4OTg3NjkwODAwNjE0MDEzOjE3MjU5NDIzNDQ6c3BfYXRmOjMwMDA2NTI4MDIwOTgzMjo6MDo6&url=%2FLive-Chinese-Tagar-Chandni-Original%2Fdp%2FB0BGQB1PR4%2Fref%3Dsr_1_1_sspa%3Fcrid%3DCFK3EYVM5K41%26dib%3DeyJ2IjoiMSJ9.8c5fR08nJRvmHOWFtr7DERhVOLesA7KwuCn6cF9EIeet52VK6jHN03EWAYaJo5CSs7FZoICYeyFV80k2E1fr2xPO9jmETBJSmuzpkq8AMX3bHd4F9HnXFswrhKCkBKUZzFgmkXyjyf8mngZiMRYecDAMpJF_KPQ1pkop5GyDImsKaY6PawKhZPs7WgOZNg75tqkdbxkF5hzncDQlNYoAPhNuhknBwR3p5w8ISrYMlORdPOBaEHQl1CAPJ1pqSw09RuZMaFiXXB5xxY9Pkunbr9ARDgPz4IObS6TQ2YRomn4.vyx9Aq3Ag-3XdL3evxVaVKOgSuG3GgIqNFwRd5Gvp1g%26dib_tag%3Dse%26keywords%3Dcrape%2Bjasmine%2Bplant%26qid%3D1725942344%26sprefix%3Dcrape%2Bjasim%2Bplant%252Caps%252C264%26sr%3D8-1-spons%26sp_csd%3Dd2lkZ2V0TmFtZT1zcF9hdGY%26psc%3D1',
           'https://www.amazon.in/sspa/click?ie=UTF8&spc=MTo3MDE5MDMxNjg3OTMyNTU1OjE3MjU5NDIzNjI6c3BfYXRmOjMwMDI3MjQ2MDAzOTkzMjo6MDo6&url=%2FUGAOO-China-Natural-Indoor-Plant%2Fdp%2FB0B74PMT39%2Fref%3Dsr_1_1_sspa%3Fcrid%3DQW8GQLEOER64%26dib%3DeyJ2IjoiMSJ9.B8k-mAUA6ruuczpZCens7ZS2kU15JBJJZ8pbKStUq-IZlmEKx-EC4nYUrnDcoF7S2dqPXZ1WrroLNyjIlgmdKv8_mxv61JnueaWbOOVot8hDpJTfSJBalpF_sZb11HpeJM-BXpxCCwPmIRgv97fEYZy2Ftr--qud046OU5OkIhN4nY8wN8VTgpzKFYR9KH5Xcy4_ok-LSvXQGntfovRaZaLn5e72I1qwx-_eyQ8upWF3-4VRxX8HTiO0og4ZjB1NYEuudl4-9rM6p0Lu2jGCwjkrcn0Naqu-LEep-ZYqyO4.XM_lfZ7dbfuRGymDnkvRtC1qO2VvJv7RyjtVJ8il9qc%26dib_tag%3Dse%26keywords%3DCommon%2Bcoleus%2Bplant%26qid%3D1725942362%26sprefix%3Dcommon%2Bcoleus%2Bplant%252Caps%252C251%26sr%3D8-1-spons%26sp_csd%3Dd2lkZ2V0TmFtZT1zcF9hdGY%26psc%3D1',
           'https://www.amazon.in/Qausain-Portulaca-Mexican-rosesun-Germination/dp/B0D86X1XCW/ref=sr_1_6?crid=2NOHSAQMKQ90A&dib=eyJ2IjoiMSJ9.zmaiGJKDc7KyaiFTKAgqYCnlucxuEnxoRN8EWpL7G7WCEoWlHmUdZFRixA-MlOtj6eZKZmgtods0nmL67yRnM1hREg1xzgZun3cXQyWMmAPi7lxdhvhyQtH56q6hAZeUgfRVze-vNBlLhPj-o32gDyeU-1kvtryQVkVZFjhPS2mbeoZYUyRxh4xSR6XtNeK8__WS2bE1MGQ7xl8f7VeClvds6zA9-fQwzktcKRHJK2QvUzrT6SkpV_n8hzhCE7l8e5b4yEmpB6QLtMCO_d2e61GB3M7QSePU825gebJnlE0.RyFXGBVkYz1SMyFexRYuIY10Gzk72YInG9rnKi8eEjs&dib_tag=se&keywords=moss+roses+plant&qid=1725942433&sprefix=moss+ros+plant%2Caps%2C242&sr=8-6',
           'https://www.amazon.in/Garden-Art-Jasmin-Nursery-Healthy/dp/B09WLKG9LJ/ref=sr_1_1_sspa?crid=1TI4M4AXVY9R7&dib=eyJ2IjoiMSJ9.ZXytfIcAsEy8fuA5FdUplIfATOJqOANrduhTANQl9UTHfxFo-d1Mp-QwAEUQ3IwM95Br74YtsC8xvKHSUspU-SO4GWMM_TfWaV9AMEi1T5axHVQ2HOU3r5qmUFLarmNE78TS6iGDhpCiw4urToGBEEp8HcKiN0FjAunFaf80Xv8evtF6HgOW-doGZJgS_bj-9aat9vgbH9_mAUpGeTu91XPiKpEMnCYyfM1YQgCT0pT9Wz-EBI8puRSeGQs_2Wl5Wti5riryQgBz1xOQF6ZZCfwkDhYGtBC5oCdRecbdJo8.Wbbj2gbvQotGxhr9wCARJJ8fgWpu2tYhfUVUgeUOYI4&dib_tag=se&keywords=arabian+jasmine+plant&qid=1725942455&sprefix=arabian+jas%2Caps%2C280&sr=8-1-spons&sp_csd=d2lkZ2V0TmFtZT1zcF9hdGY&psc=1',                                 

    ]    
    with open('data/plants.txt','r') as file:        
        f=[plant.strip('\n').lower() for plant in file.readlines()]
    return links[f.index(plant_name)]    


    