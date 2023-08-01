import Modules.MACD_Analyzer.MACD_Analyzer as Macd
import Modules.RSI_Analyzer.RSI_Analyzer as Rsi
import Modules.Stochastic_Analyzer.Stochastic_Analyzer as Stct
import pyupbit
import pandas as pd
import os
import pickle
import time

pd.set_option('mode.chained_assignment', None)  # This Action is intended in these codes.
# Original DataFrame Should not change.
# Load the list of coins from the clist file
input_file = './Modules/Get_Coins_Data/clist'
coin_list = []

with open(input_file, 'r') as file:
    for line in file:
        element = line.strip()  # Remove the newline character from the end of the line
        coin_list.append(element)

print("[INFO] COINS LOADED")

# Check if previously saved data exists
data_file_path = './Modules/Backtest/CData'
data_file = '15552d'
data = {}
use_saved_data = False
if os.path.exists(data_file_path):
    use_saved_data_option = input("Do you want to use previously saved data? (y/n): ").lower()
    if use_saved_data_option == 'y':
        use_saved_data = True
        for coin in coin_list:
            filename = "/" + coin + ".csv"
            data[coin] = pd.read_csv('Modules/Backtest/CData' + filename)
            print("[INFO] READ COIN " + coin + " COMPLETE")
else:
    data = {}

# Fetch historical data for all coins if not using saved data
if not use_saved_data:
    for coin in coin_list:
        start_time = time.perf_counter()
        data[coin] = pyupbit.get_ohlcv(coin, interval='minute5', count=15552)
        end_time = time.perf_counter()
        execution_time = end_time - start_time
        print("[INFO] REQ DONE " + coin + ",exec: ", str(round(execution_time, 2)))
        filename = str(coin) + ".csv"
        data[coin].to_csv("Modules/Backtest/CData/" + filename, sep=',', na_rep='NaN')
        print("[INFO] SAVE DONE " + coin)

print("[INFO] START BACKTEST....")

# Initial assets dictionary to track the amount of each coin
starting_balance = 10000000  # 10,000,000 KRW
initial_assets = {coin: 0 for coin in coin_list}
initial_assets['KRW'] = starting_balance
days_passed = 0
prnt_c_balance = 0

# Loop through the data to perform backtesting
for i in range(0, 6048, 1):
    for coin in coin_list:
        full_df = data[coin]
        day14_df = full_df.iloc[i:i + 4032]
        day5_df = full_df.iloc[i:i + 1440]
        day28_df = full_df.iloc[i:i + 7488]

        rsi_df, rsi, rsi_buy_signals, rsi_sell_signals, rsi_current_signal = Rsi.rsi_calc(coin, day14_df)
        macd_df, macd_line, signal_line, macd_buy_signals, macd_sell_signals, macd_current_signal = Macd.macd_calc(
            coin, day5_df)
        stct_df, k_percent, d_percent, stct_buy_signals, stct_sell_signals, stct_current_signal = Stct.stochastic_calc(
            coin, day28_df)

        # Check trading signals and perform trading action
        current_balance = initial_assets['KRW']
        if macd_current_signal == "Buy" and stct_current_signal == "Buy" and rsi_current_signal == "Buy":
            # Buy Action
            current_price = day28_df['close'].iloc[-1]  # Use the price at i+7488 as it is 28 days data
            buy_amount = current_balance * 0.1  # Buy 10% of the current balance
            coins_bought = buy_amount / current_price
            current_balance -= buy_amount
            initial_assets[coin] += coins_bought

        elif macd_current_signal == "Sell" or stct_current_signal == "Sell" and rsi_current_signal == "Sell":
            # Sell Action
            current_price = day28_df['close'].iloc[-1]  # Use the price at i+7488 as it is 28 days data
            coins_to_sell = initial_assets[coin]
            current_balance += coins_to_sell * current_price
            initial_assets[coin] = 0

        # Update the initial_assets dictionary with the current KRW balance
        initial_assets['KRW'] = current_balance
        prnt_c_balance = current_balance

    if i % 2016 == 0:
        days_passed += 1
        print(str(days_passed) + "passed. Current Balance:" + str(prnt_c_balance))
    else:
        print("[", str(round(i / 6048 * 100, 2)), "% ] ", str(i), "/ 6048")

# Calculate the total asset value in KRW based on the current prices
total_asset_value = sum([initial_assets[coin] * pyupbit.get_current_price(coin) for coin in coin_list])
for coin in coin_list:
    # Get the current price for each coin
    current_price = pyupbit.get_current_price(coin)
    # Calculate the percentage of each coin in the total asset value
    initial_assets[coin] = (initial_assets[coin] * current_price) / total_asset_value * 100

# Display the final asset percentages and current balance
print("Current Balance: ", initial_assets['KRW'], " KRW")
print("Total Balance: ", total_asset_value, " KRW")
print("Currently Owned Coins:")

for coin in coin_list:
    current_price = pyupbit.get_current_price(coin)
    current_coin_balance = initial_assets[coin] * total_asset_value / 100
    print(f"{coin}: {initial_assets[coin]:.2f}% {current_coin_balance:.2f} KRW")
