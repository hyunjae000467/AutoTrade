import Modules.MACD_Analyzer.MACD_Analyzer as Macd
import Modules.RSI_Analyzer.RSI_Analyzer as Rsi
import Modules.Stochastic_Analyzer.Stochastic_Analyzer as Stct
import pyupbit
import pandas as pd

# Load the list of coins from the clist file
input_file = './Modules/Get_Coins_Data/clist'
coin_list = []

with open(input_file, 'r') as file:
    for line in file:
        element = line.strip()  # Remove the newline character from the end of the line
        coin_list.append(element)

print("[INFO] COINS LOADED")

# Backtest duration and starting balance
backtest_duration = 6  # 6 months
starting_balance = 1000000  # 1,000,000 KRW

# Number of days for each slice
days_per_slice = 7

# Calculate the number of data points needed for 6 months
data_points_per_day = 288  # Number of data points per day (5-minute interval data)
days_per_month = 30.5  # Average number of days per month
total_data_points = int(data_points_per_day * days_per_month * backtest_duration)

# Initial assets dictionary to track the amount of each coin
initial_assets = {coin: 0 for coin in coin_list}
initial_assets['KRW'] = starting_balance

# Loop through each day for backtesting
for i in range(0, total_data_points, data_points_per_day):
    # Current balance for each day
    current_balance = initial_assets['KRW']

    # Perform the analysis for each indicator (RSI, MACD, Stochastic) for all coins
    for coin in coin_list:
        # Get historical data for the current day
        df = pyupbit.get_ohlcv(coin, interval='minute5', count=data_points_per_day)

        # Perform the analysis for each indicator (RSI, MACD, Stochastic)
        rsi_df, rsi, rsi_buy_signals, rsi_sell_signals, rsi_current_signal = Rsi.rsi_calc(coin, df)
        macd_df, macd_line, signal_line, macd_buy_signals, macd_sell_signals, macd_current_signal = Macd.macd_calc(coin, df)
        stct_df, k_percent, d_percent, stct_buy_signals, stct_sell_signals, stct_current_signal = Stct.stochastic_calc(coin, df)

        # Check trading signals and perform trading action
        if macd_current_signal == "Buy" and stct_current_signal == "Buy":
            if rsi_current_signal == "Buy":
                # Buy - 10% of the current balance
                current_price = df.iloc[-1]['close']
                buy_amount = current_balance * 0.1
                coins_bought = buy_amount / current_price
                current_balance -= buy_amount
                initial_assets[coin] += coins_bought

        elif macd_current_signal == "Sell" or stct_current_signal == "Sell":
            if rsi_current_signal == "Sell":
                # Sell - Sell all
                current_price = df.iloc[-1]['close']
                coins_to_sell = initial_assets[coin]
                current_balance += coins_to_sell * current_price
                initial_assets[coin] = 0

    # Update the initial_assets dictionary with the current KRW balance
    initial_assets['KRW'] = current_balance
    print("Current Balance : " + str(current_balance))
    print("Data " + str(i) + " Out of " + str(days_per_month * backtest_duration * data_points_per_day) + ", [" + str(
        i / (data_points_per_day * backtest_duration * days_per_month) * 100) + "%]")

# Calculate the total asset value in KRW based on the current prices
total_asset_value = sum([initial_assets[coin] * df.iloc[-1]['close'] for coin in coin_list])
for coin in coin_list:
    # Get the current price for each coin
    current_price = df.iloc[-1]['close']
    # Calculate the percentage of each coin in the total asset value
    initial_assets[coin] = (initial_assets[coin] * current_price) / total_asset_value * 100

# Display the final asset percentages
for coin, percentage in initial_assets.items():
    print(f"{coin}: {percentage:.2f}%")

# Calculate the final balance and the percentage increase
final_balance = total_asset_value
percentage_increase = (final_balance - starting_balance) / starting_balance * 100

print(f"Final Balance: {final_balance:.2f} KRW")
print(f"Percentage Increase: {percentage_increase:.2f}%")
