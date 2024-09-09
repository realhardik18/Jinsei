from flask import Flask,render_template,request
from helpers import get_city_weather

app=Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/NGO')
def NGO():
    return render_template('NGO.html')

from flask import Flask, render_template, request
import json

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/NGO')
def NGO():
    return render_template('NGO.html')


@app.route('/suggest_plant', methods=['GET', 'POST'])
def suggest_plant():
    cities = [
  "Mumbai", "Delhi", "Bangalore", "Hyderabad", "Ahmedabad", "Chennai", "Kolkata", "Surat", "Pune", "Jaipur",
  "Lucknow", "Kanpur", "Nagpur", "Indore", "Thane", "Bhopal", "Visakhapatnam", "Pimpri-Chinchwad", "Patna",
  "Vadodara", "Ghaziabad", "Ludhiana", "Agra", "Nashik", "Faridabad", "Meerut", "Rajkot", "Kalyan-Dombivli",
  "Vasai-Virar", "Varanasi", "Srinagar", "Aurangabad", "Dhanbad", "Amritsar", "Navi Mumbai", "Allahabad",
  "Ranchi", "Howrah", "Coimbatore", "Jabalpur", "Gwalior", "Vijayawada", "Jodhpur", "Madurai", "Raipur", 
  "Kota", "Guwahati", "Chandigarh", "Solapur", "Hubli–Dharwad", "Tiruchirappalli", "Bareilly", "Mysore", 
  "Moradabad", "Tiruppur", "Gurgaon", "Aligarh", "Jalandhar", "Bhubaneswar", "Salem", "Mira-Bhayandar", 
  "Warangal", "Thiruvananthapuram", "Guntur", "Bhiwandi", "Saharanpur", "Gorakhpur", "Bikaner", "Amravati", 
  "Noida", "Jamshedpur", "Bhilai", "Cuttack", "Firozabad", "Kochi", "Nellore", "Bhavnagar", "Dehradun", 
  "Durgapur", "Asansol", "Rourkela", "Nanded", "Kolhapur", "Ajmer", "Akola", "Gulbarga", "Jamnagar", 
  "Ujjain", "Loni", "Siliguri", "Jhansi", "Ulhasnagar", "Nanded-Waghala", "Bellary", "Udaipur", 
  "Bokaro Steel City", "Farrukhabad", "Malegaon", "Panipat", "Korba", "Kurnool", "Anantapur", "Bilaspur", 
  "Muzaffarnagar", "Mathura"
];

    if request.method == 'POST':
        entered_city = str(request.form.get('city', ''))
        data=get_city_weather(entered_city)
        return render_template('suggest_plant.html', data=data, cities=cities)
    return render_template('suggest_plant.html', cities=cities)

app.run(debug=True)