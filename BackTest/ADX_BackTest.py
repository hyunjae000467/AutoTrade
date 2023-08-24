from datetime import datetime, timedelta
import numpy as np
import matplotlib.pyplot as plt
import pyupbit
import os

# ADX 계산 함수
def calculate_adx(ticker, interval, period, threshold=25):
    df = pyupbit.get_ohlcv(ticker, interval=interval)
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

# ADX 그래프 생성 함수
def adx_grph(coin_name, df, adx, plus_di, minus_di, current_signal, threshold=25):
    end_time = df.index[-1]
    start_time = end_time - timedelta(hours=6)
    recent_df = df[df.index >= start_time]
    recent_adx = adx[adx.index >= start_time]
    recent_plus_di = plus_di[plus_di.index >= start_time]
    recent_minus_di = minus_di[minus_di.index >= start_time]

    plt.close('all')
    plt.figure(figsize=(12, 6))
    plt.plot(recent_df.index, recent_adx, label='ADX', color='orange')
    plt.plot(recent_df.index, recent_plus_di, label='+DI', color='blue')
    plt.plot(recent_df.index, recent_minus_di, label='-DI', color='red')
    plt.axhline(threshold, color='gray', linestyle='dashed', alpha=0.7, label='Threshold')

    buy_signals = recent_df['plus_di'] > recent_df['minus_di']
    sell_signals = recent_df['plus_di'] < recent_df['minus_di']

    plt.fill_between(recent_df.index, 0, 100, where=buy_signals, facecolor='green', alpha=0.3, label='Buy Area')
    plt.fill_between(recent_df.index, 0, 100, where=sell_signals, facecolor='red', alpha=0.3, label='Sell Area')

    plt.title('ADX and DI for {} - Last 6 Hours'.format(coin_name))
    plt.xlabel('Date')
    plt.ylabel('Value')
    plt.legend()
    plt.grid()

    current_time = datetime.now().strftime('%Y/%m/%d-%H:%M:%S')
    plt.text(0.01, 0.01, 'Current Time: {}'.format(current_time), transform=plt.gca().transAxes,
             fontsize=10, verticalalignment='bottom', bbox=dict(facecolor='white', alpha=0.5))

    img_dir = 'Modules/ADX_Analyzer/ADX_IMG_FILES'
    if not os.path.exists(img_dir):
        os.makedirs(img_dir)

    resource_location = os.path.join(img_dir, 'ADX_{}.png'.format(coin_name))
    plt.savefig(resource_location)
    
def generate_dmi_signal(df):
    # DMI 지표를 이용한 매매 신호 생성
    signals = []
    for i in range(len(df)):
        if df["plus_di"].iloc[i] > df["minus_di"].iloc[i] and df["adx"].iloc[i] > 25:
            signals.append("buy")
        elif df["plus_di"].iloc[i] < df["minus_di"].iloc[i] and df["adx"].iloc[i] > 25:
            signals.append("sell")
        else:
            signals.append("hold")
    return signals    

def backtest_adx(ticker, interval, threshold, recent_hours=6):
    end_date = datetime.now()
    start_date = end_date - timedelta(days=180)  # 백테스트 기간 설정 (최근 6개월)

    df = pyupbit.get_ohlcv(ticker, interval=interval, to=end_date, count=None)  # 백테스트 기간 동안의 모든 데이터 가져오기
    df.reset_index(inplace=True)  # 인덱스 리셋

    # ADX 계산 추가
    df, adx_values, current_signal = calculate_adx(df)

    adx = adx_values.rolling(window=14).mean()
    plus_di = df['plus_di']
    minus_di = df['minus_di']

    adx_grph(ticker, df, adx, plus_di, minus_di, current_signal)  # 그래프 생성 함수 호출
    
    signals = generate_dmi_signal(df)  # DMI 매매 신호 생성

    positions = []
    balance = 1000000  # 초기 자본금 설정
    holding = False
    
    for i in range(len(signals)):
        if signals[i] == "buy" and not holding:
            buy_price = df['close'].iloc[i]
            holding = True
        elif signals[i] == "sell" and holding:
            sell_price = df['close'].iloc[i]
            balance = balance * (sell_price / buy_price)
            holding = False
        
        positions.append(balance)
        
    return df, positions

# 백테스트 실행
ticker = "KRW-BTC"
interval = "5m"
threshold = 25
recent_hours = 6

backtest_df, backtest_positions = backtest_adx(ticker, interval, threshold, recent_hours)

# 백테스트 결과 시각화
plt.figure(figsize=(12, 6))
plt.plot(backtest_df['index'], backtest_positions, label="Backtest Performance")
plt.title("Backtest Results")
plt.xlabel("Date")
plt.ylabel("Portfolio Value")
plt.legend()
plt.grid()
plt.show()
