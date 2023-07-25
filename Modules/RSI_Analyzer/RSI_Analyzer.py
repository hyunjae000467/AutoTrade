import pyupbit
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
from datetime import datetime, timedelta


def rsi_calc(coin_name):
    pd.set_option('display.float_format', lambda x: '%.2f' % x)

    # Fetch data for the last 14 days (14 days * 24 hours * 12 5-minute intervals per hour)
    df = pyupbit.get_ohlcv(coin_name, interval='minute5', count=4032)

    df['변화량'] = df['close'] - df['close'].shift(1)
    df['상승폭'] = np.where(df['변화량'] >= 0, df['변화량'], 0)
    df['하락폭'] = np.where(df['변화량'] < 0, df['변화량'].abs(), 0)

    df['AU'] = df['상승폭'].ewm(span=14, min_periods=14, adjust=False).mean()
    df['AD'] = df['하락폭'].ewm(span=14, min_periods=14, adjust=False).mean()
    df['RSI'] = df['AU'] / (df['AU'] + df['AD']) * 100

    # Generate Buy and Sell Signals
    buy_signals = df['RSI'] < 30
    sell_signals = df['RSI'] > 70

    current_signal = "Neutral"
    if buy_signals.iloc[-1]:
        current_signal = "Buy"
    elif sell_signals.iloc[-1]:
        current_signal = "Sell"

    return df, df['RSI'], buy_signals, sell_signals, current_signal


def rsi_grph(coin_name, recent_hours=6):
    df, rsi, buy_signals, sell_signals, current_signal = rsi_calc(coin_name)

    # Get the end time of the data
    end_time = df.index[-1]

    # Calculate the start time for the last 6 hours
    start_time = end_time - timedelta(hours=recent_hours)

    # Slice the data for the last 6 hours
    recent_df = df[df.index >= start_time]
    recent_rsi = rsi[rsi.index >= start_time]
    recent_buy_signals = buy_signals[buy_signals.index >= start_time]
    recent_sell_signals = sell_signals[sell_signals.index >= start_time]

    plt.close('all')
    plt.figure(figsize=(12, 6))
    plt.plot(recent_df.index, recent_rsi, label='RSI', color='b')
    plt.axhline(y=70, color='r', linestyle='--', label='Overbought (70)')
    plt.axhline(y=30, color='g', linestyle='--', label='Oversold (30)')

    # Plot buy and sell signals
    plt.plot(recent_df.index[recent_buy_signals], recent_rsi[recent_buy_signals], '^', markersize=10, color='g',
             label='Buy Signal')
    plt.plot(recent_df.index[recent_sell_signals], recent_rsi[recent_sell_signals], 'v', markersize=10, color='r',
             label='Sell Signal')

    plt.title('RSI Graph for {} - Last 6 Hours'.format(coin_name))
    plt.xlabel('Date')
    plt.ylabel('RSI Value')
    plt.legend()
    plt.grid(True)

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

    # Create the 'RSI_IMG_FILES' directory if it does not exist
    img_dir = 'Modules/RSI_Analyzer/RSI_IMG_FILES'
    if not os.path.exists(img_dir):
        os.makedirs(img_dir)

    resource_location = os.path.join(img_dir, 'RSI_{}.png'.format(coin_name))
    plt.savefig(resource_location)
    # print("RSI Done")

    return recent_df, recent_rsi, recent_buy_signals, recent_sell_signals, current_signal
