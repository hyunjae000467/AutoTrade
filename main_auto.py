# Not for use of Normal Occasions. This file is made for Python Github Workflow.

import math

import Modules.MACD_Analyzer.MACD_Analyzer as Macd
import Modules.RSI_Analyzer.RSI_Analyzer as Rsi
import Modules.Stochastic_Analyzer.Stochastic_Analyzer as Stct
import Modules.Tensorflow_Analyzer.Tensorflow_Analyzer as Tf
input_file = './Modules/Get_Coins_Data/clist'
coin_list = []

with open(input_file, 'r') as file:
    for line in file:
        element = line.strip()  # Remove the newline character from the end of the line
        coin_list.append(element)

print("[INFO] Coins Loaded")
# print(coin_list)
print("Input 1 for RSI Analyze")
print("Input 2 for MACD Analyze")
print("Input 3 for Stochastic Oscillator Analyze")
print("Input 4 for Tensorflow Prediction")
print("Input 5 for ALL")
mode = 5  # Change Mode for RSI, MACD, STOCHASTIC OSCILLATOR

# 1 is for RSI
# 2 is for MACD
# 3 is for STOCHASTIC OSCILLATOR
# 4 is for Tensorflow
# 5 is for ALL
progress = 0

for coin in coin_list:
    if mode != 5:
        progress += 1
    if mode == 1 or mode == 5:
        rsi_df, rsi_df_2, rsi_buy_signals, rsi_sell_signals, rsi_current_signal = Rsi.rsi_calc(coin)
        Rsi.rsi_grph(coin)
        if mode == 5:
            progress += (1 / 4)
        print("[", round(progress / 30 * 100), "%] RSI Done on coin ", coin, ", Coin is currently on",
              rsi_current_signal, "position.")
    if mode == 2 or mode == 5:
        macd_df, macd_line, macd_signal_line, macd_buy_signal, macd_sell_signal, macd_current_signal = Macd.macd_calc(
            coin)
        Macd.macd_grph(coin, macd_df, macd_line, macd_signal_line, macd_buy_signal, macd_sell_signal,
                       macd_current_signal)
        if mode == 5:
            progress += (1 / 4)
        print("[", round(progress / 30 * 100), "%] MACD Done on coin ", coin, ", Coin is currently on",
              macd_current_signal, "position.")
    if mode == 3 or mode == 5:
        stct_df, k_percent, d_percent, stct_buy_signals, stct_sell_signals, stct_current_signal = Stct.stochastic_calc(
            coin,
            'minute5',
            1440)
        Stct.stochastic_grph(coin, stct_df, k_percent, d_percent, stct_buy_signals, stct_sell_signals,
                             stct_current_signal)
        if mode == 5:
            progress += (1 / 4)
        print("[", round(progress / 30 * 100), "%] STCT Done on coin ", coin, ", Coin is currently on",
              stct_current_signal, "position.")
    if mode == 4 or mode == 5:
        Tf.asset_price_prediction(coin_name=coin, interval='minute5', count=1440)
        if mode == 5:
            progress += (1 / 4)
        print("[", round(progress / 30 * 100), "%] TF Done on coin ", coin)
    if mode == 0 or math.isnan(mode) == True:
        print("[STOP] Program Ended | Cause : Mode is on 0, or NaN")
        break
