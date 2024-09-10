from flask import Flask,render_template,request,redirect, url_for,session
from helpers import get_city_weather,best_match,retrieve_plant_data

app = Flask(__name__)
app.secret_key = 'hIUHiuhIUhu'

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/NGO')
def NGO():
    return render_template('NGO.html')

@app.route('/suggest_plant', methods=['GET', 'POST'])
def suggest_plant():
    if request.method == 'POST':
        entered_city = str(request.form.get('city', '')).strip()  # Get the entered city and strip whitespace
        if entered_city:  # Only proceed if the city is not empty
            print(entered_city)
            weather = get_city_weather(entered_city)
            data = best_match(weather['temperature'], weather['relative_humidity'])
            plants = list()
            for d in data:
                plants.append(retrieve_plant_data(plant=d.lower()))
            print(data)
            return render_template('suggest_plant.html', data=plants,Edata=weather)
        else:
            # No city was entered; render the template with no data
            return render_template('suggest_plant.html', data=None)

    # For GET requests or when no valid city was submitted
    return render_template('suggest_plant.html', data=None)

@app.route('/manure_creation')
def manure():
    return render_template('manure.html')

@app.route('/scan')
def scan():
    return render_template('scan.html')

@app.route('/future')
def future():
    return render_template('future.html')

app.run(debug=True)
