import os
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from prophet import Prophet
import pyupbit

def get_target_price(ticker, k):
    """변동성 돌파 전략으로 매수 목표가 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="day", count=2)
    target_price = df.iloc[0]['close'] + (df.iloc[0]['high'] - df.iloc[0]['low']) * k
    return target_price

def get_current_price(ticker):
    """현재가 조회"""
    return pyupbit.get_orderbook(ticker=ticker)["orderbook_units"][0]["ask_price"]

predicted_close_price = 0

def prophet_calc(ticker, interval='minute60'):
    """Prophet으로 당일 종가 가격 예측"""
    global predicted_close_price
    df = pyupbit.get_ohlcv(ticker, interval=interval)
    df = df.reset_index()
    df['ds'] = df['index']
    df['y'] = df['close']
    data = df[['ds', 'y']]
    model = Prophet()
    model.fit(data)
    future = model.make_future_dataframe(periods=24, freq='H')
    forecast = model.predict(future)
    closeDf = forecast[forecast['ds'] == forecast.iloc[-1]['ds'].replace(hour=9)]
    if len(closeDf) == 0:
        closeDf = forecast[forecast['ds'] == data.iloc[-1]['ds'].replace(hour=9)]
    closeValue = closeDf['yhat'].values[0]
    predicted_close_price = closeValue
    target_price = get_target_price(ticker, 0.5)
    current_price = get_current_price(ticker)
    current_signal = "Neutral"  # Default signal is Neutral

    if target_price < current_price < predicted_close_price:
        current_signal = "Buy"
    elif current_price < target_price:
        current_signal = "Sell"

    return current_signal, df, predicted_close_price  # Returning current_signal and DataFrame

def backtest_prophet(ticker, interval='minute60'):
    # Get historical data
    df = pyupbit.get_ohlcv(ticker, interval=interval)
    
    # Perform prediction and get current signal
    current_signal, df, predicted_close_price = prophet_calc(ticker, interval)
    
    # Initialize portfolio balance and position
    balance = 1000000  # Initial balance
    position = 0  # Initial position
    buy_price = 0  # Initialize buy price
    
    # Lists to track portfolio value over time
    portfolio_values = [balance]
    
    for i in range(len(df)):
        if current_signal == "Buy" and position == 0:
            buy_price = df['close'].iloc[i]
            position = balance / buy_price
        
        elif current_signal == "Sell" and position > 0:
            sell_price = df['close'].iloc[i]
            balance = position * sell_price
            position = 0
        
        portfolio_values.append(balance)
    
    # Plot portfolio value over time
    plt.figure(figsize=(12, 6))
    plt.plot(df['ds'], portfolio_values, label="Portfolio Value")
    plt.title("Prophet Backtest Results for {}".format(ticker))
    plt.xlabel("Date")
    plt.ylabel("Portfolio Value")
    plt.legend()
    plt.grid()
    plt.show()

# 백테스트 실행
ticker = "KRW-BTC"
interval = "60m"
backtest_prophet(ticker, interval)