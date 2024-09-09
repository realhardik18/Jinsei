from flask import Flask,render_template

app=Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/NGO')
def NGO():
    return render_template('NGO.html')

app.run(debug=True)