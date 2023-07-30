import os
from datetime import datetime
from datetime import timedelta

import matplotlib.pyplot as plt
import pyupbit


def stochastic_calc(coin_name, interval="minute5", count=1440, backtest=0):
    # Get historical price data from pyupbit
    df = pyupbit.get_ohlcv(coin_name, interval=interval, count=count)

    # Calculate Stochastic Oscillator
    high = df['high']
    low = df['low']
    close = df['close']

    # Stochastic Oscillator Formula
    lowest_low = low.rolling(5).min()
    highest_high = high.rolling(5).max()
    k_percent = 100 * (close - lowest_low) / (highest_high - lowest_low)
    d_percent = k_percent.rolling(3).mean()

    # Generate Buy and Sell Signals
    buy_signals = (k_percent > d_percent) & (k_percent.shift() < d_percent.shift())
    sell_signals = (k_percent < d_percent) & (k_percent.shift() > d_percent.shift())

    current_signal = "Neutral"
    if buy_signals.iloc[-1]:
        current_signal = "Buy"
    elif sell_signals.iloc[-1]:
        current_signal = "Sell"

    return df, k_percent, d_percent, buy_signals, sell_signals, current_signal


def stochastic_grph(coin_name, df, k_percent, d_percent, buy_signals, sell_signals, current_signal, recent_hours=6):
    # Get the end time of the data
    end_time = df.index[-1]

    # Calculate the start time for the last 12 hours
    start_time = end_time - timedelta(hours=recent_hours)

    # Slice the data for the last 12 hours
    recent_df = df[df.index >= start_time]
    recent_k_percent = k_percent[k_percent.index >= start_time]
    recent_d_percent = d_percent[d_percent.index >= start_time]
    recent_buy_signals = buy_signals[buy_signals.index >= start_time]
    recent_sell_signals = sell_signals[sell_signals.index >= start_time]

    plt.close('all')
    plt.figure(figsize=(12, 6))
    plt.plot(recent_df.index, recent_k_percent, label='%K')
    plt.plot(recent_df.index, recent_d_percent, label='%D')

    # Plot horizontal lines at 80 and 20
    plt.axhline(80, color='red', linestyle='dashed', alpha=0.7)
    plt.axhline(20, color='green', linestyle='dashed', alpha=0.7)

    # Plot buy and sell signals
    plt.plot(recent_df.index[recent_buy_signals], recent_k_percent[recent_buy_signals], '^', markersize=10, color='g',
             label='Buy Signal')
    plt.plot(recent_df.index[recent_sell_signals], recent_k_percent[recent_sell_signals], 'v', markersize=10, color='r',
             label='Sell Signal')

    plt.title('Stochastic Oscillator for {} - Last 6 Hours'.format(coin_name))
    plt.xlabel('Date')
    plt.ylabel('Percentage')
    plt.legend()
    plt.grid()

    # Add small text on the left bottom with current time
    current_time = datetime.now().strftime('%Y/%m/%d-%H:%M:%S')
    plt.text(0.01, 0.01, 'Current Time: {}'.format(current_time), transform=plt.gca().transAxes,
             fontsize=10, verticalalignment='bottom', bbox=dict(facecolor='white', alpha=0.5))

    # Add a text box on the top right
    box_text = ""
    text_color = "gray"
    if current_signal == "Buy":
        box_text = "BUY"
        text_color = "red"
    elif current_signal == "Sell":
        box_text = "SELL"
        text_color = "green"
    elif current_signal == "Neutral":
        box_text = "Neutral"

    plt.text(0.98, 0.98, box_text, transform=plt.gca().transAxes, fontsize=12, color = text_color,
             verticalalignment='top', horizontalalignment='right', bbox=dict(facecolor='white', edgecolor='black'))

    # Create the 'RSI_IMG_FILES' directory if it does not exist
    img_dir = 'Modules/Stochastic_Analyzer/Stochastic_IMG_FILES'
    if not os.path.exists(img_dir):
        os.makedirs(img_dir)

    resource_location = os.path.join(img_dir, 'Stochastic_{}.png'.format(coin_name))
    plt.savefig(resource_location)
    # print("RSI Done")
