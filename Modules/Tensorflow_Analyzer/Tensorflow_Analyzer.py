from datetime import datetime
import tensorflow as tf
import numpy as np
import matplotlib.pyplot as plt
import pyupbit
import os
def asset_price_prediction(coin_name, interval, count, test_size=0.2):
    # Get price data from pyupbit
    df = pyupbit.get_ohlcv(coin_name, interval=interval, count=count)

    # Extract price and time data
    prices = df['close'].values.reshape(-1, 1)
    times = df.index

    # Preprocess the data
    train_size = int(len(prices) * (1 - test_size))
    train_data, test_data = prices[:train_size], prices[train_size:]

    # Normalize the data
    data_min, data_max = np.min(prices), np.max(prices)
    train_data = (train_data - data_min) / (data_max - data_min)
    test_data = (test_data - data_min) / (data_max - data_min)

    # Create input and output sequences for the neural network
    def create_sequences(data, sequence_length):
        sequences = []
        for i in range(len(data) - sequence_length):
            sequences.append(data[i:i + sequence_length])
        return np.array(sequences)

    sequence_length = 10  # Adjust this value based on your data
    X_train = create_sequences(train_data, sequence_length)
    y_train = train_data[sequence_length:]

    # Define the neural network architecture
    model = tf.keras.Sequential([
        tf.keras.layers.Dense(64, activation='relu', input_shape=(sequence_length,)),
        tf.keras.layers.Dense(32, activation='relu'),
        tf.keras.layers.Dense(1)
    ])

    # Compile the model
    model.compile(optimizer='adam', loss='mean_squared_error')

    # Train the model
    model.fit(X_train, y_train, epochs=50, batch_size=16)

    # Predict using the test data
    X_test = create_sequences(test_data, sequence_length)
    y_pred = model.predict(X_test)

    # Rescale the predicted data to the original price range
    y_pred = y_pred * (data_max - data_min) + data_min

    # Create a chart with real-time dates
    plt.figure(figsize=(12, 6))
    plt.plot(times[train_size + sequence_length:], prices[train_size + sequence_length:], label='True Price', color='blue')
    plt.plot(times[train_size + sequence_length:], y_pred, label='Predicted Price', color='red')
    plt.xlabel('Time')
    plt.ylabel('Price')
    plt.title(f'{coin_name} Price Prediction')
    plt.legend()
    # Add small text on the left bottom with current time
    current_time = datetime.now().strftime('%Y/%m/%d-%H:%M:%S')
    plt.text(0.01, 0.01, 'Current Time: {}'.format(current_time), transform=plt.gca().transAxes,
             fontsize=10, verticalalignment='bottom', bbox=dict(facecolor='white', alpha=0.5))

    # Create the 'MACD_IMG_FILES' directory if it does not exist
    img_dir = 'Modules/Tensorflow_Analyzer/Tensorflow_IMG_FILES'
    if not os.path.exists(img_dir):
        os.makedirs(img_dir)

    resource_location = os.path.join(img_dir, 'TF_{}.png'.format(coin_name))
    plt.savefig(resource_location)
    # print("MACD Done")
