import pyupbit
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
from datetime import datetime


def rsi_calc(coin_name):
    pd.set_option('display.float_format', lambda x: '%.2f' % x)
    df = pyupbit.get_ohlcv(coin_name)

    df['변화량'] = df['close'] - df['close'].shift(1)
    df['상승폭'] = np.where(df['변화량'] >= 0, df['변화량'], 0)
    df['하락폭'] = np.where(df['변화량'] < 0, df['변화량'].abs(), 0)

    # welles moving average
    df['AU'] = df['상승폭'].ewm(alpha=1 / 14, min_periods=14).mean()
    df['AD'] = df['하락폭'].ewm(alpha=1 / 14, min_periods=14).mean()
    # df['RS'] = df['AU'] / df['AD']
    # df['RSI'] = 100 - (100 / (1 + df['RS']))
    df['RSI'] = df['AU'] / (df['AU'] + df['AD']) * 100

    return df[['RSI']]


def rsi_grph(coin_name):
    df = rsi_calc(coin_name)
    plt.close('all')  # closes all the figure windows
    plt.figure(figsize=(12, 6))
    plt.plot(df.index, df['RSI'], label='RSI', color='b')
    plt.axhline(y=70, color='r', linestyle='--', label='Overbought (70)')
    plt.axhline(y=30, color='g', linestyle='--', label='Oversold (30)')
    plt.title('RSI Graph for {}'.format(coin_name))
    # print('RSI Graph for {}'.format(coin_name))
    plt.xlabel('Date')
    plt.ylabel('RSI Value')
    plt.legend()
    plt.grid(True)

    # Add small text on the left bottom with current time
    current_time = datetime.now().strftime('%Y/%m/%d-%H:%M:%S')
    plt.text(0.01, 0.01, 'Current Time: {}'.format(current_time), transform=plt.gca().transAxes,
             fontsize=10, verticalalignment='bottom', bbox=dict(facecolor='white', alpha=0.5))

    # Create the 'RSI_IMG_FILES' directory if it does not exist
    img_dir = 'Modules/RSI_Analyzer/RSI_IMG_FILES'
    if not os.path.exists(img_dir):
        os.makedirs(img_dir)

    resource_location = os.path.join(img_dir, 'RSI_{}.png'.format(coin_name))
    plt.savefig(resource_location)
    print("Done")
    # plt.show()
