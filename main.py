import pyupbit
import Modules.RSI_Analyzer.RSI_Analyzer as rsi
input_file = './Modules/Get_Coins_Data/clist'
coin_list = []

with open(input_file, 'r') as file:
    for line in file:
        element = line.strip()  # Remove the newline character from the end of the line
        coin_list.append(element)

print(coin_list)

for coin in coin_list:
    rsi.rsi_grph(coin)
