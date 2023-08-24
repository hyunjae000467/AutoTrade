from datetime import datetime, timedelta
import numpy as np
import matplotlib.pyplot as plt
import pyupbit
import os

def calculate_dmi(df):
    # DMI 계산 및 반환
    df["up_move"] = df["high"] - df["high"].shift(1)
    df["down_move"] = df["low"].shift(1) - df["low"]
    df["plus_dm"] = 0.0
    df["minus_dm"] = 0.0
    df.loc[df["up_move"] > df["down_move"], "plus_dm"] = df["up_move"]
    df.loc[df["down_move"] > df["up_move"], "minus_dm"] = df["down_move"]
    df["plus_di"] = 100 * df["plus_dm"].rolling(window=14).sum() / df["high"].rolling(window=14).sum()
    df["minus_di"] = 100 * df["minus_dm"].rolling(window=14).sum() / df["low"].rolling(window=14).sum()
    df["dx"] = 100 * abs(df["plus_di"] - df["minus_di"]) / (df["plus_di"] + df["minus_di"])
    df["adx"] = df["dx"].rolling(window=14).mean()
    return df  # DataFrame을 반환

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

def dmi_grph(coin_name, df, recent_hours=6):
    # 그래프 그리기
    df = calculate_dmi(df)  # DMI 계산 추가
    end_time = df.index[-1]

    start_time = end_time - timedelta(hours=recent_hours)

    recent_df = df[df.index >= start_time]
    
    plt.close('all')
    plt.figure(figsize=(12, 6))
    
    plt.plot(recent_df.index, recent_df["plus_di"], label='+DI')
    plt.plot(recent_df.index, recent_df["minus_di"], label='-DI')
    plt.plot(recent_df.index, recent_df["adx"], label='ADX')

    # 그래프 스타일 및 레이블 설정
    plt.title('DMI for {} - Last {} Hours'.format(coin_name, recent_hours))
    plt.xlabel('Date')
    plt.ylabel('Value')
    plt.legend()
    plt.grid()

    # 그래프 저장 및 메시지 전송
    img_dir = 'Modules/DMI_Analyzer/DMI_IMG_FILES'
    if not os.path.exists(img_dir):
        os.makedirs(img_dir)

    resource_location = os.path.join(img_dir, 'DMI_{}.png'.format(coin_name))
    plt.savefig(resource_location)