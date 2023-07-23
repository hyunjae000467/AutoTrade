import pandas as pd
import numpy as np
import pyupbit
import time

# 업비트 원화 거래 가능한 티커명 조회
ticker_names = pyupbit.get_tickers(fiat='KRW')
len(ticker_names)

# 일봉 데이터 다운로드
for ticker_name in ticker_names:
    print(f'download {ticker_name}')
    df = pyupbit.get_ohlcv(ticker_name)
    df.to_csv(f'CData/{ticker_name}.csv', encoding='cp949')
    time.sleep(0.1)
# 거래대금 정보 가져오기
tickers = []
for ticker_name in ticker_names:
    filename = f'CData/{ticker_name}.csv'
    df = pd.read_csv(filename)
    yesterday = df.iloc[-2]
    tickers.append([ticker_name, yesterday['value']])

# 거래대금 상위 30개의 종목만 리스트업
top_k = 30
tickers = sorted(tickers, key=lambda x: x[1], reverse=True)
tickers = tickers[:top_k]

output_name = './clist'
with open(output_name, 'w+') as file:
    for i in tickers:
        if not isinstance(i, np.float64):  # Check if the element is not of type numpy.float64
            if isinstance(i, list):  # Check if it's a list
                i = i[0]  # Take the first element (string) of the list
            if not isinstance(i, str):  # Check if it's not already a string
                i = str(i)  # Convert to string if it's not
            file.write(i + "\n")

# EOF


