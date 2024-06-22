from datetime import datetime, timedelta

import streamlit as st
import pandas as pd
import requests

API_KEY = st.secrets["WEATHER_API_KEY"]

# Define the mapping dictionary
api_weather_code_mapping = {
    1000: 'sun',
    1003: 'sun',  # "Partly cloudy" considered as sun
    1006: 'sun',  # "Cloudy" considered as sun
    1009: 'sun',  # "Overcast" considered as sun
    1030: 'fog',
    1063: 'rain',  # "Patchy rain possible" considered as rain
    1066: 'snow',  # "Patchy snow possible" considered as snow
    1069: 'snow',  # "Patchy sleet possible" considered as snow
    1072: 'drizzle',  # "Patchy freezing drizzle possible" considered as drizzle
    1087: 'rain',  # "Thundery outbreaks possible" considered as rain
    1114: 'snow',  # "Blowing snow" considered as snow
    1117: 'snow',  # "Blizzard" considered as snow
    1135: 'fog',
    1147: 'fog',  # "Freezing fog" considered as fog
    1150: 'drizzle',  # "Patchy light drizzle" considered as drizzle
    1153: 'drizzle',  # "Light drizzle" considered as drizzle
    1168: 'drizzle',  # "Freezing drizzle" considered as drizzle
    1171: 'drizzle',  # "Heavy freezing drizzle" considered as drizzle
    1180: 'rain',  # "Patchy light rain" considered as rain
    1183: 'rain',  # "Light rain" considered as rain
    1186: 'rain',  # "Moderate rain at times" considered as rain
    1189: 'rain',  # "Moderate rain" considered as rain
    1192: 'rain',  # "Heavy rain at times" considered as rain
    1195: 'rain',  # "Heavy rain" considered as rain
    1198: 'drizzle',  # "Light freezing rain" considered as drizzle
    1201: 'drizzle',  # "Moderate or heavy freezing rain" considered as drizzle
    1204: 'snow',  # "Light sleet" considered as snow
    1207: 'snow',  # "Moderate or heavy sleet" considered as snow
    1210: 'snow',  # "Patchy light snow" considered as snow
    1213: 'snow',  # "Light snow" considered as snow
    1216: 'snow',  # "Patchy moderate snow" considered as snow
    1219: 'snow',  # "Moderate snow" considered as snow
    1222: 'snow',  # "Patchy heavy snow" considered as snow
    1225: 'snow',  # "Heavy snow" considered as snow
    1237: 'snow',  # "Ice pellets" considered as snow
    1240: 'rain',  # "Light rain shower" considered as rain
    1243: 'rain',  # "Moderate or heavy rain shower" considered as rain
    1246: 'rain',  # "Torrential rain shower" considered as rain
    1249: 'snow',  # "Light sleet showers" considered as snow
    1252: 'snow',  # "Moderate or heavy sleet showers" considered as snow
    1255: 'snow',  # "Light snow showers" considered as snow
    1258: 'snow',  # "Moderate or heavy snow showers" considered as snow
    1261: 'snow',  # "Light showers of ice pellets" considered as snow
    1264: 'snow',  # "Moderate or heavy showers of ice pellets" considered as snow
    1273: 'rain',  # "Patchy light rain with thunder" considered as rain
    1276: 'rain',  # "Moderate or heavy rain with thunder" considered as rain
    1279: 'snow',  # "Patchy light snow with thunder" considered as snow
    1282: 'snow',  # "Moderate or heavy snow with thunder" considered as snow
}

csv_weather_code_mapping = {0: 'drizzle', 1: 'rain', 2: 'sun', 3: 'snow', 4: 'fog'}


def download_weather(date):
    # Download the data from the API
    global _result
    url = f'http://api.weatherapi.com/v1/history.json?key={API_KEY}&q=Seattle&dt={date}'
    response = requests.get(url)
    if response.status_code == 200:
        # Parse the response as JSON
        json_response = response.json()
        _result = json_response['forecast']['forecastday'][0]['day']
        date = json_response['forecast']['forecastday'][0]['date']
    else:
        print(f"Request failed with status code {response.status_code}")

    return [date,
            _result['totalprecip_mm'],
            _result['maxtemp_c'],
            _result['mintemp_c'],
            _result['maxwind_kph'],
            api_weather_code_mapping[_result['condition']['code']]]


def prepare_sequence():
    # Get today's date
    today = datetime.today()

    # Generate a list of the last ten 20 days (invert)
    last_ten_days = [(today - timedelta(days=i)).strftime('%Y-%m-%d') for i in range(20)][::-1]

    weather = []

    for date in last_ten_days:
        weather.append(download_weather(date))

    weather = pd.DataFrame(weather)
    weather.columns = ['date', 'precipitation', 'temp_max', 'temp_min', 'wind', 'weather']

    return weather