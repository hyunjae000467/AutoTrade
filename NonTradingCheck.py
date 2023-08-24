import math

import Modules.MACD_Analyzer.MACD_Analyzer_old as Macd
import Modules.RSI_Analyzer.RSI_Analyzer_old as Rsi
import Modules.Stochastic_Analyzer.Stochastic_Analyzer_old as Stct
import Modules.Tensorflow_Analyzer.Tensorflow_Analyzer as Tf
import Modules.ADX_Analyzer.ADX_Analyzer as Adx
import Modules.Prophet_Analyzer.Prophet_Analyzer as Prpht

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
print("Input 5 for ADX Analyze")
print("Input 6 for Propeht Analyze")
print("Input 7 for ALL")
mode = int(input("Select Mode : "))  # Change Mode for RSI, MACD, STOCHASTIC OSCILLATOR

# 1 is for RSI
# 2 is for MACD
# 3 is for STOCHASTIC OSCILLATOR
# 4 is for Tensorflow
# 5 is for ADX
# 6 is for PROPHET
# 7 is for ALL
progress = 0
total_mode_count = 7
for coin in coin_list:
    if mode != total_mode_count:
        progress += 1
    if mode == 1 or mode == total_mode_count:
        rsi_df, rsi_df_2, rsi_buy_signals, rsi_sell_signals, rsi_current_signal = Rsi.rsi_calc(coin)
        Rsi.rsi_grph(coin)
        if mode == total_mode_count:
            progress += (1 / (total_mode_count - 1))
        print("[", round(progress / (total_mode_count - 1) * 10), "%] RSI Done on coin ", coin, ", Coin is currently on",
              rsi_current_signal, "position.")
    if mode == 2 or mode == total_mode_count:
        macd_df, macd_line, macd_signal_line, macd_buy_signal, macd_sell_signal, macd_current_signal = Macd.macd_calc(
            coin)
        Macd.macd_grph(coin, macd_df, macd_line, macd_signal_line, macd_buy_signal, macd_sell_signal,
                       macd_current_signal)
        if mode == total_mode_count:
            progress += (1 / (total_mode_count - 1))
        print("[", round(progress / (total_mode_count - 1) * 10), "%] MACD Done on coin ", coin, ", Coin is currently on",
              macd_current_signal, "position.")
    if mode == 3 or mode == total_mode_count:
        stct_df, k_percent, d_percent, stct_buy_signals, stct_sell_signals, stct_current_signal = Stct.stochastic_calc(
            coin,
            'minute5',
            1440)
        Stct.stochastic_grph(coin, stct_df, k_percent, d_percent, stct_buy_signals, stct_sell_signals,
                             stct_current_signal)
        if mode == total_mode_count:
            progress += (1 / (total_mode_count - 1))
        print("[", round(progress / (total_mode_count - 1) * 10), "%] STCT Done on coin ", coin, ", Coin is currently on",
              stct_current_signal, "position.")
    if mode == 4 or mode == total_mode_count:
        Tf.asset_price_prediction(coin_name=coin, interval='minute5', count=1440)
        if mode == total_mode_count:
            progress += (1 / (total_mode_count - 1))
        print("[", round(progress / (total_mode_count - 1) * 10), "%] TF Done on coin ", coin)
    if mode == 5 or mode == total_mode_count:
        adx_df, adx, adx_current_signal= Adx.calculate_adx(coin, 'minute5', 14)
        plus_di = adx_df['plus_di']
        minus_di = adx_df['minus_di']
        Adx.adx_grph(coin, adx_df, adx, plus_di, minus_di, adx_current_signal, threshold=25)
        if mode == total_mode_count:
            progress += (1 / (total_mode_count - 1))
        print("[", round(progress / (total_mode_count - 1) * 10), "%] ADX Done on coin ", coin)
    if mode == 6 or mode == total_mode_count:
        prophet_current_signal, prophet_df, prophet_predicted_close_price = Prpht.prophet_calc(coin)
        Prpht.prophet_grph(coin,prophet_df,prophet_predicted_close_price,prophet_current_signal)
        if mode == total_mode_count:
            progress += (1 / (total_mode_count - 1))
        print("[", round(progress / (total_mode_count - 1) * 10), "%] ADX Done on coin ", coin)
    if mode == 0 or math.isnan(mode) == True:
        print("[STOP] Program Ended | Cause : Mode is on 0, or NaN")
        break
