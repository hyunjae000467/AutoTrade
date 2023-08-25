import os
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np


def calculate_dmi(df):
    # Calculate True Range (TR)
    high = df['high']
    low = df['low']
    close = df['close']

    df['TR'] = np.maximum.reduce([high - low, abs(high - close.shift(1)), abs(low - close.shift(1))])

    # Calculate Plus Directional Movement (+DM) and Minus Directional Movement (-DM)
    df['UpMove'] = high - high.shift(1)
    df['DownMove'] = low.shift(1) - low
    df['PlusDM'] = np.where((df['UpMove'] > df['DownMove']) & (df['UpMove'] > 0), df['UpMove'], 0)
    df['MinusDM'] = np.where((df['DownMove'] > df['UpMove']) & (df['DownMove'] > 0), df['DownMove'], 0)

    # Calculate Average True Range (ATR)
    atr_period = 14  # Adjust as needed
    df['ATR'] = df['TR'].rolling(atr_period).mean()

    # Calculate Plus Directional Indicator (+DI) and Minus Directional Indicator (-DI)
    di_period = 14  # Adjust as needed
    df['PlusDI'] = df['PlusDM'].rolling(di_period).sum() / df['ATR']
    df['MinusDI'] = df['MinusDM'].rolling(di_period).sum() / df['ATR']

    # Calculate Average Directional Index (ADX)
    adx_period = 14  # Adjust as needed
    df['DX'] = abs(df['PlusDI'] - df['MinusDI']) / (df['PlusDI'] + df['MinusDI'])
    df['ADX'] = df['DX'].rolling(adx_period).mean()

    # Generate Buy and Sell Signals
    df['Buy_Signal'] = (df['PlusDI'] > df['MinusDI']) & (df['ADX'] > 25)
    df['Sell_Signal'] = (df['PlusDI'] < df['MinusDI']) & (df['ADX'] > 25)

    df['Signal'] = "Neutral"
    df.loc[df['Buy_Signal'], 'Signal'] = "Buy"
    df.loc[df['Sell_Signal'], 'Signal'] = "Sell"

    current_signal = df['Signal'].iloc[-1]

    return df, current_signal


def dmi_grph(coin_name, df, buy_signals, sell_signals, current_signal, recent_hours=6):
    # Get the end time of the data
    end_time = df.index[-1]

    # Calculate the start time for the last N hours
    start_time = end_time - timedelta(hours=recent_hours)

    # Slice the data for the last N hours
    recent_df = df[df.index >= start_time]
    recent_buy_signals = buy_signals[buy_signals.index >= start_time]
    recent_sell_signals = sell_signals[sell_signals.index >= start_time]

    plt.close('all')
    plt.figure(figsize=(12, 6))

    # Plot +DI, -DI, and ADX
    plt.plot(recent_df.index, recent_df['PLUS_DI_14'], label='+DI')
    plt.plot(recent_df.index, recent_df['MINUS_DI_14'], label='-DI')
    plt.plot(recent_df.index, recent_df['ADX_14'], label='ADX')

    # Plot buy and sell signals
    plt.plot(recent_df.index[recent_buy_signals], recent_df['ADX_14'][recent_buy_signals], '^', markersize=10,
             color='g',
             label='Buy Signal')
    plt.plot(recent_df.index[recent_sell_signals], recent_df['ADX_14'][recent_sell_signals], 'v', markersize=10,
             color='r',
             label='Sell Signal')

    plt.title('DMI for {} - Last {} Hours'.format(coin_name, recent_hours))
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

    # Create the 'DMI_IMG_FILES' directory if it does not exist
    img_dir = 'Modules/DMI_Analyzer/DMI_IMG_FILES'
    if not os.path.exists(img_dir):
        os.makedirs(img_dir)

    resource_location = os.path.join(img_dir, 'DMI_{}.png'.format(coin_name))
    plt.savefig(resource_location)
    # print("DMI Done")
