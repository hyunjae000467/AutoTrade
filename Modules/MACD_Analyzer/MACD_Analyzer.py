import os
from datetime import datetime
from datetime import timedelta

import matplotlib.pyplot as plt
import pyupbit


def macd_calc(coin_name, interval="minute10", count=3744):
    # Get historical price data from pyupbit
    df = pyupbit.get_ohlcv(coin_name, interval=interval, count=count)

    # Calculate MACD
    close = df['close']

    # Calculate 12-day EMA
    ema_12 = close.ewm(span=12, adjust=False).mean()

    # Calculate 26-day EMA
    ema_26 = close.ewm(span=26, adjust=False).mean()

    # Calculate MACD Line
    macd_line = ema_12 - ema_26

    # Calculate 9-day EMA of MACD Line
    signal_line = macd_line.ewm(span=9, adjust=False).mean()

    # Generate Buy and Sell Signals
    buy_signals = (macd_line > signal_line) & (macd_line.shift() < signal_line.shift())
    sell_signals = (macd_line < signal_line) & (macd_line.shift() > signal_line.shift())

    current_signal = "Neutral"
    if buy_signals.iloc[-1]:
        current_signal = "Buy"
    elif sell_signals.iloc[-1]:
        current_signal = "Sell"

    return df, macd_line, signal_line, buy_signals, sell_signals, current_signal


def macd_grph(coin_name, df, macd_line, signal_line, buy_signals, sell_signals, current_signal, recent_hours=6):
    # Get the end time of the data
    end_time = df.index[-1]

    # Calculate the start time for the last 12 hours
    start_time = end_time - timedelta(hours=recent_hours)

    # Slice the data for the last 12 hours
    recent_df = df[df.index >= start_time]
    recent_macd_line = macd_line[macd_line.index >= start_time]
    recent_signal_line = signal_line[signal_line.index >= start_time]
    recent_buy_signals = buy_signals[buy_signals.index >= start_time]
    recent_sell_signals = sell_signals[sell_signals.index >= start_time]

    plt.close('all')
    plt.figure(figsize=(12, 6))
    plt.plot(recent_df.index, recent_macd_line, label='MACD Line')
    plt.plot(recent_df.index, recent_signal_line, label='Signal Line')

    # Plot zero line
    plt.axhline(0, color='gray', linestyle='dashed', alpha=0.7)

    # Plot buy and sell signals
    plt.plot(recent_df.index[recent_buy_signals], recent_macd_line[recent_buy_signals], '^', markersize=10, color='g',
             label='Buy Signal')
    plt.plot(recent_df.index[recent_sell_signals], recent_macd_line[recent_sell_signals], 'v', markersize=10, color='r',
             label='Sell Signal')

    plt.title('MACD for {} - Last 6 Hours'.format(coin_name))
    plt.xlabel('Date')
    plt.ylabel('Value')
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

    plt.text(0.98, 0.98, box_text, transform=plt.gca().transAxes, fontsize=12, color=text_color,
             verticalalignment='top', horizontalalignment='right', bbox=dict(facecolor='white', edgecolor='black'))

    # Create the 'MACD_IMG_FILES' directory if it does not exist
    img_dir = 'Modules/MACD_Analyzer/MACD_IMG_FILES'
    if not os.path.exists(img_dir):
        os.makedirs(img_dir)

    resource_location = os.path.join(img_dir, 'MACD_{}.png'.format(coin_name))
    plt.savefig(resource_location)
    # print("MACD Done")
