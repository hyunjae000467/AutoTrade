import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import pyupbit
import os
from datetime import datetime

def stochastic_calc(coin_name, interval="minute5", count=100):
    # Get historical price data from pyupbit
    df = pyupbit.get_ohlcv(coin_name, interval=interval, count=count)

    # Calculate Stochastic Oscillator
    high = df['high']
    low = df['low']
    close = df['close']

    # Stochastic Oscillator Formula
    lowest_low = low.rolling(14).min()
    highest_high = high.rolling(14).max()
    k_percent = 100 * (close - lowest_low) / (highest_high - lowest_low)
    d_percent = k_percent.rolling(3).mean()

    # Generate Buy and Sell Signals
    buy_signals = (k_percent > d_percent) & (k_percent.shift() < d_percent.shift())
    sell_signals = (k_percent < d_percent) & (k_percent.shift() > d_percent.shift())

    return df, k_percent, d_percent, buy_signals, sell_signals


def stochastic_grph(coin_name, df, k_percent, d_percent, buy_signals, sell_signals):
    plt.close('all')
    plt.figure(figsize=(12, 6))
    plt.plot(df.index, k_percent, label='%K')
    plt.plot(df.index, d_percent, label='%D')

    # Plot horizontal lines at 80 and 20
    plt.axhline(80, color='red', linestyle='dashed', alpha=0.7)
    plt.axhline(20, color='green', linestyle='dashed', alpha=0.7)

    # Plot buy and sell signals
    plt.plot(df.index[buy_signals], k_percent[buy_signals], '^', markersize=10, color='g', label='Buy Signal')
    plt.plot(df.index[sell_signals], k_percent[sell_signals], 'v', markersize=10, color='r', label='Sell Signal')

    plt.title('Stochastic Oscillator')
    plt.xlabel('Date')
    plt.ylabel('Percentage')
    plt.legend()
    plt.grid()

    # Add small text on the left bottom with current time
    current_time = datetime.now().strftime('%Y/%m/%d-%H:%M:%S')
    plt.text(0.01, 0.01, 'Current Time: {}'.format(current_time), transform=plt.gca().transAxes,
             fontsize=10, verticalalignment='bottom', bbox=dict(facecolor='white', alpha=0.5))

    # Create the 'RSI_IMG_FILES' directory if it does not exist
    img_dir = 'Modules/Stochastic_Analyzer/Stochastic_IMG_FILES'
    if not os.path.exists(img_dir):
        os.makedirs(img_dir)

    resource_location = os.path.join(img_dir, 'Stochastic_{}.png'.format(coin_name))
    plt.savefig(resource_location)
    # print("RSI Done")