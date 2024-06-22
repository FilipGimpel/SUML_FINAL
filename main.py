import copy
from datetime import datetime, timedelta

import numpy as np
import pandas as pd
import streamlit as st

from util import csv_weather_code_mapping, prepare_sequence
from weathermodel import load, preprocess_data


def predict(_model, _sequence, _scaler):
    # Use the model to make a prediction
    _prediction = _model.predict(_sequence)

    # Undo the parameter scaling
    _prediction = _scaler.inverse_transform(_prediction)

    # Round the prediction to an integer
    _prediction[:, 5] = (np.rint(_prediction[:, 5]))

    # convert the prediction to a list to keep numbers and string for display
    _prediction = _prediction.tolist()

    # decode the weather labels using given dictionary
    for row in _prediction:
        row[5] = csv_weather_code_mapping[row[5]]

    return _prediction


def dataframe_prediction(_prediction):
    today = datetime.today()
    prediction = []

    # Add the date to the prediction array
    for i, row in enumerate(_prediction):
        # Generate the date for the next day
        next_day = (today + timedelta(days=i + 1)).strftime('%Y-%m-%d')
        prediction.append([next_day, max(0,row[1]), row[2], row[3], row[4], row[5]])

    weather = pd.DataFrame(prediction)
    weather.columns = ['date', 'precipitation', 'temp_max', 'temp_min', 'wind', 'weather']

    return weather


def main():
    model = load()
    past_weather = prepare_sequence()
    past_weather_to_print = copy.deepcopy(past_weather)

    past_weather_processed, le, scaler = preprocess_data(past_weather)
    prediction = predict(model, past_weather_processed, scaler)

    st.set_page_config(page_title="Seattle Weather Prediction")
    overview = st.container()

    with overview:
        st.title("Seattle Weather Prediction")
        st.write("This app uses historical weather data ("
                 "https://www.kaggle.com/datasets/ananthr1/weather-prediction/data) to train a model, then fetches the "
                 "weather from the last ten days using https://www.weatherapi.com/ and predicts the weather for the "
                 "next ten days.")
        st.subheader("Last ten days of weather:")
        st.write(past_weather_to_print.tail(10))

        st.subheader("The weather prediction for the next ten days is as follows:")
        st.write(dataframe_prediction(prediction))


if __name__ == "__main__":
    main()
