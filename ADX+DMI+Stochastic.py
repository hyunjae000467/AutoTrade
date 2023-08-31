import ADX_BackTest as Adx
import DMI_BackTest as Dmi
import Stochastic_BackTest as Stct
import pyupbit
import pandas as pd
import matplotlib.pyplot as plt
from pandas import DataFrame

# 7달치 데이터 불러오기
input_file = 'clist'
coin_list = []
worth_history = []  # Initialize a list to store the history of worth

with open(input_file, 'r') as file:
    for line in file:
        element = line.strip()  # Remove the newline character from the end of the line
        coin_list.append(element)
balance = 100000000 #KRW
init_balance = 100000000 #KRW
coins_held = 0
coin_bought = "KRW-XXX"
print("[INFO] Coins Loaded")
read_y_n = input("[CONF] Do you wish to read files? [y/n] : ")
if read_y_n == 'y':
    for coin in coin_list:
        old_data_df = pyupbit.get_ohlcv(coin, interval='minute5', count=62496)
        old_data_df.to_csv(f'DATA_FILES/'+coin + '_old_data.csv')
        print("[WARN] DONE GETTING ",coin)

already_bought = False
for count in range(8928, 62496, 12):
    already_bought = False

    for coin in coin_list:
        if already_bought:
            break
        if coin_bought != coin and coin_bought != "KRW-XXX":
            point = 0
            continue
        current_df = pd.read_csv(f'DATA_FILES/'+coin+'_old_data.csv')
        adx_df = current_df
        dmi_df = current_df
        stct_df = current_df
        # 규격에 맞게 데이터프레임 가공
        adx_df.loc[count - 13:count]
        dmi_df.loc[count - 13:count]
        stct_df.loc[count - 1439:count]
        # 계산
        _, _, adx_current_sig = Adx.calculate_adx(adx_df)
        _, dmi_current_sig = Dmi.calculate_dmi(dmi_df)
        _, _, _, _, _, stct_current_sig = Stct.stochastic_calc(stct_df)
        # 판단
        point = 0
        if adx_current_sig == "Buy":
            point = point + 1
        if dmi_current_sig == "Buy":
            point += 1
        if stct_current_sig == "Buy":
            point += 1

        if adx_current_sig == "Netural":
            point = point + 0
        if dmi_current_sig == "Netural":
            point += 0
        if stct_current_sig == "Netural":
            point += 0

        if adx_current_sig == "Sell":
            point = point + -1
        if dmi_current_sig == "Sell":
            point += -1
        if stct_current_sig == "Sell":
            point += -1

        # -3 ~ -2 : Strong Sell Signal
        # -1 ~ 1 : Weak Signal
        # 2 ~ 3 : Strong Buy Signal

        #Current Price =
        if -3 <= point <= -2:
            if coin == coin_bought:
                balance += coins_held * current_df['close'].loc[count]  # Update balance with the selling amount
                coins_held = 0  # Reset the coins held to zero
                coin_bought = "KRW-XXX"
        elif -1 <= point <= 1:
            pass
        elif 2 <= point <= 3:
            if coins_held == 0:
                coins_bought = balance / current_df['close'].loc[count]  # Calculate the amount of coins bought
                coins_held += coins_bought  # Update the coins held with the buying amount
                balance -= coins_bought * current_df['close'].loc[count]  # Update balance by deducting the buying amount
                coin_bought = coin
                already_bought = True
            #Buy Code goes here
        print("[INFO] ",count," passed out of 62496, current balance is ",balance,", coins held ",coins_held, ", Holding Points",point,"for coin ",coin)
        point = 0
        worth = current_df['close'].loc[count] * coins_held
        worth_history.append(worth)  # Record the worth at each iteration
        if worth < init_balance * 0.8:
            balance += coins_held * current_df['close'].loc[count]
            coins_held = 0
            already_bought = False
            coin_bought = "KRW-XXX"

print("Final balance:", balance, "KRW")
print("Coins held:", coins_held)
plt.plot(worth_history, label="Portfolio Worth")
plt.xlabel("Iteration")
plt.ylabel("Portfolio Worth (KRW)")
plt.legend()
plt.title("Portfolio Worth Over Time")
plt.show()

print("Final balance:", balance, "KRW")
print("Coins held:", coins_held)
