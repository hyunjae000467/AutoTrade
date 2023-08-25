from datetime import datetime, timedelta
import numpy as np
import matplotlib.pyplot as plt
import pyupbit
import os


def calculate_adx(df, period=14, threshold=25):
    df['true_range'] = np.maximum(df['high'] - df['low'], np.maximum(abs(df['high'] - df['close'].shift(1)),
                                                                     abs(df['low'] - df['close'].shift(1))))
    df['up_move'] = df['high'] - df['high'].shift(1)
    df['down_move'] = df['low'].shift(1) - df['low']
    df['plus_dm'] = np.where((df['up_move'] > df['down_move']) & (df['up_move'] > 0), df['up_move'], 0)
    df['minus_dm'] = np.where((df['down_move'] > df['up_move']) & (df['down_move'] > 0), df['down_move'], 0)
    df['tr_sum'] = df['true_range'].rolling(window=period).sum()
    df['plus_di'] = (df['plus_dm'].rolling(window=period).sum() / df['tr_sum']) * 100
    df['minus_di'] = (df['minus_dm'].rolling(window=period).sum() / df['tr_sum']) * 100
    df['adx'] = (abs(df['plus_di'] - df['minus_di']) / (df['plus_di'] + df['minus_di'])) * 100

    current_plus_di = df['plus_di'].iloc[-1]
    current_minus_di = df['minus_di'].iloc[-1]
    current_signal = "Neutral"
    if current_plus_di > current_minus_di:
        current_signal = "Buy" if current_plus_di > threshold else "Neutral"
    elif current_plus_di < current_minus_di:
        current_signal = "Sell" if current_minus_di > threshold else "Neutral"

    return df, df['adx'], current_signal