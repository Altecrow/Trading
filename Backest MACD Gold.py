import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv(rf"C:\Users\Romain\Desktop\Trade\Codes\Databases\XAU_1M.csv")
df['datetime'] = pd.to_datetime(df['Date'] + ' ' + df['Time'], format='%Y.%m.%d %H:%M')
df['seconds_since_epoch'] = (df['datetime'] - pd.Timestamp("1970-01-01")) // pd.Timedelta('1s')
df['reconstructed_datetime'] = pd.to_datetime(df['seconds_since_epoch'], unit='s')
df = df.set_index("reconstructed_datetime")
duplicated_data = df.index.duplicated(keep="last")
del df["Date"]
del df["Time"]
df = df[~duplicated_data]

df["ma26"] = df["Close"].ewm(span = 26, adjust = False).mean()
df["ma12"] = df["Close"].ewm(span = 12, adjust = False).mean()
df["MACD_line"] = df["ma12"] - df["ma26"]
df["signal_line"] = df["MACD_line"].ewm(span = 9, adjust = False).mean()

df["buy_signal"] = False
df["sell_signal"] = False

df["crossover"] = df["MACD_line"] - df["signal_line"]

df.loc[(df["crossover"] > 0) & (df["crossover"].shift(1) <= 0), "buy_signal"] = True

df.loc[(df["crossover"] < 0) & (df["crossover"].shift(1) >= 0), "sell_signal"] = True

balance = 1000
position = None
balances = []

for index, row in df.iterrows():
    #Buy condition
    if position is None and row["buy_signal"] is True:
        buy_price = row["Close"]
        pos_size = balance
        position = {
            "buy_price": buy_price,
            "pos_size": pos_size,
        }
        #print(f"{index} - Buy XAU for {pos_size}$ at {buy_price}$")
    
    elif position is not None and row["sell_signal"] is True:
        sell_price = row["Close"]
        trade_result = (sell_price - position["buy_price"]) / position["buy_price"]
        balance = balance + trade_result * position["pos_size"]
        #print(f"{index} - Sell XAU for {balance}$ at {sell_price}$ ({round(trade_result * 100, 2)} %)")
        position = None
    
    balances.append(balance)  

df["balance_over_time"] = balances

print(f"{round((((balance / 1000) - 1) * 100), 2)} %")

evo = df.loc[df.index[-1], "Close"] / df.loc[df.index[0], "Close"] 

print(f"{round((evo - 1)*100)} %")

plt.figure(figsize=(12, 6))

plt.plot(df.index, df["Close"] * 2.60, label="Gold Price (Close)", color="gold")

plt.plot(df.index, df["balance_over_time"], label="Balance", color="blue")

plt.title("Evolution of Gold Price and Balance Over Time")
plt.xlabel("Time")
plt.ylabel("Value (USD)")
plt.legend()
plt.grid()

plt.tight_layout()
plt.show()