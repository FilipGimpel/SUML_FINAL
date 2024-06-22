import pandas as pd
import numpy as np
from keras import Sequential
from keras.src.layers import LSTM, Dense
from keras.src.saving import load_model
from sklearn.preprocessing import MinMaxScaler, LabelEncoder


MODEL_PATH = 'model.keras'


def preprocess_data(_df):
    # df = pd.read_csv('seattle-weather.xls')
    # ['drizzle' 'rain' 'sun' 'snow' 'fog']

    # Let's extract the month and encode it as a categorical variable
    _df['month'] = pd.to_datetime(_df['date']).dt.month

    # Encode categorical columns
    le = LabelEncoder()
    _df['weather'] = le.fit_transform(_df['weather'])

    # Normalize the data
    scaler = MinMaxScaler(feature_range=(0, 1))
    scaled_data = scaler.fit_transform(_df[['month', 'precipitation', 'temp_max', 'temp_min', 'wind', 'weather']])

    # Convert data into sequences
    sequence_length = 10
    result = []
    for index in range(len(scaled_data) - sequence_length):
        result.append(scaled_data[index: index + sequence_length])

    return np.array(result), le, scaler


def train_and_save_model(_df):
    result, le, scaler = preprocess_data(_df)

    # Split data into train
    train_size = round(0.9 * result.shape[0])
    train = result[:int(train_size), :]
    np.random.shuffle(train)

    x_train = train[:, :-1]
    y_train = train[:, -1]

    # Build the model
    model = Sequential()
    model.add(LSTM(64, input_shape=(x_train.shape[1], x_train.shape[2]), return_sequences=True))
    model.add(LSTM(32, return_sequences=False))
    model.add(Dense(10, activation='linear'))
    model.add(Dense(y_train.shape[1], activation='linear'))

    model.compile(loss='mse', optimizer='rmsprop')

    # Train the model
    model.fit(x_train, y_train, batch_size=32, epochs=20, validation_split=0.1)

    # save the model
    model.save(MODEL_PATH)

    # Evaluate the model
    # model.evaluate(x_test, y_test)


def load():
    # if model exists in MODEL_PATH load it, if not, train and save it
    try:
        model = load_model(MODEL_PATH)
    except:
        _df = pd.read_csv('seattle-weather.xls')
        train_and_save_model(_df)
        model = load_model(MODEL_PATH)
    return model
