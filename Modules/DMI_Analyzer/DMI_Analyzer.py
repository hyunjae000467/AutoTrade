import os
from datetime import datetime
from datetime import timedelta

import matplotlib.pyplot as plt
import pyupbit
import talib

def dmi_calc(df):
    # Calculate DMI
    high = df['high']
    low = df['low']
    close = df['close']

    # Calculate DMI using TA-Lib
    dmi_data = talib.DX(high, low, close)
    adx = talib.ADX(high, low, close, timeperiod=14)
    minus_di = talib.MINUS_DI(high, low, close, timeperiod=14)
    plus_di = talib.PLUS_DI(high, low, close, timeperiod=14)

    # Generate Buy and Sell Signals
    buy_signals = (plus_di > minus_di) & (adx > 25)
    sell_signals = (plus_di < minus_di) & (adx > 25)

    current_signal = "Neutral"
    if buy_signals.iloc[-1]:
        current_signal = "Buy"
    elif sell_signals.iloc[-1]:
        current_signal = "Sell"

    return df, dmi_data, plus_di, minus_di, buy_signals, sell_signals, current_signal

def dmi_grph(coin_name, df, dmi_data, plus_di, minus_di, buy_signals, sell_signals, current_signal, recent_hours=6):
    # Get the end time of the data
    end_time = df.index[-1]

    # Calculate the start time for the last N hours
    start_time = end_time - timedelta(hours=recent_hours)

    # Slice the data for the last N hours
    recent_df = df[df.index >= start_time]
    recent_dmi_data = dmi_data[dmi_data.index >= start_time]
    recent_plus_di = plus_di[plus_di.index >= start_time]
    recent_minus_di = minus_di[minus_di.index >= start_time]
    recent_buy_signals = buy_signals[buy_signals.index >= start_time]
    recent_sell_signals = sell_signals[sell_signals.index >= start_time]

    plt.close('all')
    plt.figure(figsize=(12, 6))
    plt.plot(recent_df.index, recent_plus_di, label='+DI')
    plt.plot(recent_df.index, recent_minus_di, label='-DI')
    plt.plot(recent_df.index, recent_dmi_data, label='DX')

    # Plot buy and sell signals
    plt.plot(recent_df.index[recent_buy_signals], recent_dmi_data[recent_buy_signals], '^', markersize=10, color='g',
             label='Buy Signal')
    plt.plot(recent_df.index[recent_sell_signals], recent_dmi_data[recent_sell_signals], 'v', markersize=10, color='r',
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
