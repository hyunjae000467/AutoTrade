import os
from datetime import datetime, timedelta
import numpy as np
import matplotlib.pyplot as plt
import pyupbit

def macd_calc(df):
    close = df['close']
    ema_12 = close.ewm(span=12, adjust=False).mean()
    ema_26 = close.ewm(span=26, adjust=False).mean()
    macd_line = ema_12 - ema_26
    signal_line = macd_line.ewm(span=9, adjust=False).mean()
    buy_signals = (macd_line > signal_line) & (macd_line.shift() < signal_line.shift())
    sell_signals = (macd_line < signal_line) & (macd_line.shift() > signal_line.shift())
    
    current_signal = "Neutral"
    if buy_signals.iloc[-1]:
        current_signal = "Buy"
    elif sell_signals.iloc[-1]:
        current_signal = "Sell"
    
    return df, macd_line, signal_line, buy_signals, sell_signals, current_signal

def macd_grph(coin_name, df, macd_line, signal_line, buy_signals, sell_signals, current_signal, recent_hours=6):
    end_time = df.index[-1]
    start_time = end_time - timedelta(hours=recent_hours)
    recent_df = df[df.index >= start_time]
    recent_macd_line = macd_line[macd_line.index >= start_time]
    recent_signal_line = signal_line[signal_line.index >= start_time]
    recent_buy_signals = buy_signals[buy_signals.index >= start_time]
    recent_sell_signals = sell_signals[sell_signals.index >= start_time]
    
    plt.close('all')
    plt.figure(figsize=(12, 6))
    plt.plot(recent_df.index, recent_macd_line, label='MACD Line')
    plt.plot(recent_df.index, recent_signal_line, label='Signal Line')
    plt.axhline(0, color='gray', linestyle='dashed', alpha=0.7)
    plt.plot(recent_df.index[recent_buy_signals], recent_macd_line[recent_buy_signals], '^', markersize=10, color='g',
             label='Buy Signal')
    plt.plot(recent_df.index[recent_sell_signals], recent_macd_line[recent_sell_signals], 'v', markersize=10, color='r',
             label='Sell Signal')
    plt.title('MACD for {} - Last {} Hours'.format(coin_name, recent_hours))
    plt.xlabel('Date')
    plt.ylabel('Value')
    plt.legend()
    plt.grid()
    
    current_time = datetime.now().strftime('%Y/%m/%d-%H:%M:%S')
    plt.text(0.01, 0.01, 'Current Time: {}'.format(current_time), transform=plt.gca().transAxes,
             fontsize=10, verticalalignment='bottom', bbox=dict(facecolor='white', alpha=0.5))
    
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
    
    img_dir = 'MACD_IMG_FILES'
    if not os.path.exists(img_dir):
        os.makedirs(img_dir)
    resource_location = os.path.join(img_dir, 'MACD_{}.png'.format(coin_name))
    plt.savefig(resource_location)

def backtest_macd(ticker, interval, recent_hours=6):
    end_date = datetime.now()
    start_date = end_date - timedelta(days=180)
    
    df = pyupbit.get_ohlcv(ticker, interval=interval, to=end_date, count=None)
    df.reset_index(inplace=True)
    df, macd_line, signal_line, buy_signals, sell_signals, current_signal = macd_calc(df)
    
    macd_grph(ticker, df, macd_line, signal_line, buy_signals, sell_signals, current_signal, recent_hours)
    
    positions = []
    balance = 1000000
    holding = False
    
    for i in range(len(buy_signals)):
        if buy_signals[i] and not holding:
            buy_price = df['close'].iloc[i]
            holding = True
        elif sell_signals[i] and holding:
            sell_price = df['close'].iloc[i]
            balance = balance * (sell_price / buy_price)
            holding = False
        
        positions.append(balance)
        
    return df, positions

ticker = "KRW-BTC"
interval = "5m"
recent_hours = 6

backtest_df, backtest_positions = backtest_macd(ticker, interval, recent_hours)

plt.figure(figsize=(12, 6))
plt.plot(backtest_df['index'], backtest_positions, label="Backtest Performance")
plt.title("Backtest Results")
plt.xlabel("Date")
plt.ylabel("Portfolio Value")
plt.legend()
plt.grid()
plt.show()