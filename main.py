import Modules.MACD_Analyzer.MACD_Analyzer as Macd
import Modules.RSI_Analyzer.RSI_Analyzer as Rsi
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
        rsi_df, rsi_df_2, rsi_buy_signals, rsi_sell_signals, rsi_current_signal = Rsi.rsi_calc(coin)
        Rsi.rsi_grph(coin)
        print("[", round(progress / 30 * 100), "%] RSI Done on coin ", coin, ", Coin is currently on",
              rsi_current_signal, "position.")
    elif mode == 2:
        Macd.macd_grph(coin)
        print("[", round(progress / 30 * 100), "%] MACD Done on coin ", coin)
    elif mode == 3:
        stct_df, k_percent, d_percent, stct_buy_signals, stct_sell_signals, stct_current_signal = Stct.stochastic_calc(
            coin,
            'minute5',
            1440)
        Stct.stochastic_grph(coin, stct_df, k_percent, d_percent, stct_buy_signals, stct_sell_signals,
                             stct_current_signal)
        print("[", round(progress / 30 * 100), "%] STCT Done on coin ", coin, ", Coin is currently on",
              stct_current_signal, "position.")
    else:
        print("[STOP] Program Ended | Cause : Mode is on 0, or NaN")
        break
