import requests
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy 

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///weather.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = "Secret Key"

db = SQLAlchemy(app)

class City(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)

#to check city exist or not requested from the api, before adding to the db
def get_weather_data(city):
    url = f'http://api.openweathermap.org/data/2.5/weather?q={ city }&units=imperial&appid=271d1234d3f497eed5b1d80a07b3fcd1'

#request from url
    r = requests.get(url).json()
#return request as json object
    return r

@app.route('/')
def index_get():
#for taking all cities in the table
    cities = City.query.all()
#API endpoints. Query is going to be blank {} which reprensts city. units are going to be imperial i.e fahreneit. app id is getting from weathermap.


    weather_data = []

    for city in cities:
# r stands for response/request. output will be in json format. it will send req to the api getting weather for that particular city. url.format will insert the city in the url above
#for getting actual city name, city name is used

        r = get_weather_data(city.name)
        print(r)

#weather has many params like humidity, temp, press so we are using dictionary. only below 4 params we want from website weathermap to show on webpg, thatswhy we mentioned 4 below.
#each cities in this loop is going to send req to the apigetting weather for that particular city and is going to this dictionary
#below city.name is used instead of city, otherwise city1,city2 will be displayed
        weather = {
            'city' : city.name,
            'temperature' : r['main']['temp'],
            'description' : r['weather'][0]['description'],
            'icon' : r['weather'][0]['icon'],
        }
#weather[0] means first item of list weather
        weather_data.append(weather)

#because weather of every cities will be displayed thru rendertemplate
    return render_template('weather.html', weather_data=weather_data)


@app.route('/', methods= ['POST'])
def index_post():
    err_msg = ''

    new_city = request.form.get('city')
#to check if user sent something
    if new_city:
#now to check entered city is there or not in the db and to get first result if exist, if there then dont add.
        existing_city= City.query.filter_by(name=new_city).first()
        if not existing_city:
            new_city_data = get_weather_data(new_city)
            if new_city_data['cod'] == 200:
                new_city_obj = City(name=new_city)
                db.session.add(new_city_obj)
                db.session.commit()
            else:
                err_msg = 'City does not exist in the world!'
        else:
            err_msg = 'City already exist in the database!'

    if err_msg:
        flash(err_msg, 'error')
    else:
        flash('City added successfully')


    return redirect(url_for('index_get'))
# because weather of every cities will be displayed thru render_template

@app.route('/delete/<name>')
def delete_city(name):
    city = City.query.filter_by(name=name).first()
    db.session.delete(city)
    db.session.commit()

    flash(f'Successfully deleted { city.name }', 'success')
    return redirect(url_for('index_get'))


if __name__ == "__main__":
    app.run(debug =True)
