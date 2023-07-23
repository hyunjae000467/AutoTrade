import pyupbit
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
from datetime import datetime
from functools import lru_cache


@lru_cache(maxsize=32)  # Cache the result of the function to avoid redundant calculations
def get_price_data(coin_name, interval='minute5', count=10080):
    return pyupbit.get_ohlcv(coin_name, interval=interval, count=count)


def macd_calc(coin_name):
    # Get the price data using cached function
    df = get_price_data(coin_name)

    # Calculate the 12-day and 26-day exponential moving averages (EMA)
    ema_12 = df['close'].ewm(span=12, adjust=False).mean()
    ema_26 = df['close'].ewm(span=26, adjust=False).mean()

    # Calculate the MACD line
    macd_line = ema_12 - ema_26

    # Calculate the 9-day EMA of the MACD line (Signal line)
    signal_line = macd_line.ewm(span=9, adjust=False).mean()

    # Calculate the MACD Histogram (the difference between the MACD line and the Signal line)
    macd_histogram = macd_line - signal_line

    # Create a new DataFrame with the calculated MACD components as columns
    macd_df = pd.DataFrame({
        'close': df['close'],
        'macd_line': macd_line,
        'signal_line': signal_line,
        'macd_histogram': macd_histogram
    })

    return macd_df


def macd_grph(coin_name):
    # Get the MACD data using the optimized macd_calc() function
    df = macd_calc(coin_name)
    plt.close('all')  # closes all the figure windows
    # Plotting the MACD graph
    plt.figure(figsize=(12, 6))
    # plt.plot(df.index, df['close'], label='Close Price', color='blue')
    plt.bar(df.index, df['macd_histogram'], label='MACD Histogram', color='gray', alpha=0.5)
    plt.plot(df.index, df['macd_line'], label='MACD Line', color='red')
    plt.plot(df.index, df['signal_line'], label='Signal Line', color='green')

    plt.title(f"MACD Analysis for {coin_name}")
    plt.xlabel('Date')
    plt.ylabel('MACD')
    plt.legend()
    plt.grid(True)
    # Add small text on the left bottom with current time
    current_time = datetime.now().strftime('%Y/%m/%d-%H:%M:%S')
    plt.text(0.01, 0.01, 'Current Time: {}'.format(current_time), transform=plt.gca().transAxes,
             fontsize=10, verticalalignment='bottom', bbox=dict(facecolor='white', alpha=0.5))

    # Create the 'RSI_IMG_FILES' directory if it does not exist
    img_dir = 'Modules/MACD_Analyzer/MACD_IMG_FILES'
    if not os.path.exists(img_dir):
        os.makedirs(img_dir)

    resource_location = os.path.join(img_dir, 'MACD_{}.png'.format(coin_name))
    plt.savefig(resource_location)
    print("MACD Done")
    # plt.show()
