import pyupbit
import Modules.RSI_Analyzer.RSI_Analyzer as Rsi
import Modules.MACD_Analyzer.MACD_Analyzer as Macd
import Modules.Stochastic_Analyzer.Stochastic_Analyzer as Stct

input_file = './Modules/Get_Coins_Data/clist'
coin_list = []

with open(input_file, 'r') as file:
    for line in file:
        element = line.strip()  # Remove the newline character from the end of the line
        coin_list.append(element)

print("[INFO] Coins Loaded")
# print(coin_list)

mode = int(input("Select Mode : "))  # Change Mode for RSI, MACD, STOCHASTIC OSCILLATOR

# 1 is for RSI
# 2 is for MACD
# 3 is for STOCHASTIC OSCILLATOR


progress = 0

for coin in coin_list:
    progress += 1
    if mode == 1:
        Rsi.rsi_grph(coin)
        print("[", round(progress / 30 * 100), "%] RSI Done on coin ", coin)
    elif mode == 2:
        Macd.macd_grph(coin)
        print("[", round(progress / 30 * 100), "%] MACD Done on coin ", coin)
    elif mode == 3:
        df, k_percent, d_percent, buy_signals, sell_signals = Stct.stochastic_calc(coin, 'minute5', 1440)
        Stct.stochastic_grph(coin, df, k_percent, d_percent, buy_signals, sell_signals)
        print("[", round(progress / 30 * 100), "%] STCT Done on coin ", coin)
    else:
        print("[STOP] Program Ended | Cause : Mode is on 0, or NaN")
        break
