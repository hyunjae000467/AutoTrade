import os
from datetime import datetime, timedelta

import matplotlib.pyplot as plt
import pyupbit


def stochastic_calc(coin_name, df):

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

    return df, k_percent, d_percent, buy_signals, sell_signals


def stochastic_backtest(coin_name, df, k_percent, d_percent, buy_signals, sell_signals):
    # Initialize variables
    initial_balance = 1000000  # Initial balance in KRW
    balance = initial_balance
    coins = 0
    in_position = False
    buy_price = 0
    total_trades = 0
    winning_trades = 0

    # Loop through the data
    for i in range(len(df)):
        if buy_signals[i] and not in_position:
            coins = balance / df['close'][i]
            balance = 0
            buy_price = df['close'][i]
            in_position = True
            total_trades += 1
        elif sell_signals[i] and in_position:
            balance = coins * df['close'][i]
            coins = 0
            in_position = False
            if df['close'][i] > buy_price:
                winning_trades += 1

    # Calculate metrics
    final_balance = balance + (coins * df['close'].iloc[-1])
    total_profit = final_balance - initial_balance
    win_rate = winning_trades / total_trades if total_trades > 0 else 0

    return final_balance, total_profit, win_rate


# Load data using pyupbit or provide your own data
coin_name = 'BTC'
df = pyupbit.get_ohlcv(coin_name, interval="minute60")

# Calculate Stochastic Oscillator
df, k_percent, d_percent, buy_signals, sell_signals = stochastic_calc(coin_name, df)

# Perform backtest
final_balance, total_profit, win_rate = stochastic_backtest(coin_name, df, k_percent, d_percent, buy_signals, sell_signals)

print(f"Final Balance: {final_balance:.2f} KRW")
print(f"Total Profit: {total_profit:.2f} KRW")
print(f"Win Rate: {win_rate:.2%}")