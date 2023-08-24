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



def prophet_grph(ticker, df, predicted_close_price, current_signal):
    plt.close('all')
    plt.figure(figsize=(12, 6))

    # Plot actual close prices
    plt.plot(df['ds'], df['y'], label='Actual Close Price', color='blue')

    # Plot predicted close prices
    predicted_prices = [predicted_close_price] * len(df)
    plt.plot(df['ds'], predicted_prices, label='Predicted Close Price', color='red', linestyle='dotted')
    plt.title('Prophet Price Prediction for {}'.format(ticker))
    plt.xlabel('Date')
    plt.ylabel('Price')
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

    # Create the image directory if it does not exist
    img_dir = 'Modules/Prophet_Analyzer/Prophet_IMG_FILES'
    if not os.path.exists(img_dir):
        os.makedirs(img_dir)
    resource_location = os.path.join(img_dir, 'Prophet_{}.png'.format(ticker))
    plt.savefig(resource_location)