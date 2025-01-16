import pandas as pd

crypto_list = ["ADA", "BCH", "BNB", "BTC", "ETC", "ETH", "LINK", "LTC", "XLM", "XRP"]
data_path = rf"C:\Users\Romain\Desktop\Trade\Codes\Databases Training\Cryptos"
df_list = {}

for crypto in crypto_list:
    df_list[crypto] = pd.read_csv(rf"{data_path}\{crypto}-USDT.csv")
    df_list[crypto]["date"] = pd.to_datetime(df_list[crypto]["date"], unit="ms")
    df_list[crypto] = df_list[crypto].set_index("date")
    duplicated_data = df_list[crypto].index.duplicated(keep="last")
    df_list[crypto] = df_list[crypto][~duplicated_data]

for crypto, df in df_list.items():
    df["ma26"] = df["close"].ewm(span = 26, adjust = False).mean()
    df["ma12"] = df["close"].ewm(span = 12, adjust = False).mean()
    df["MACD_line"] = df["ma12"] - df["ma26"]
    df["signal_line"] = df["MACD_line"].ewm(span = 9, adjust = False).mean()

    df["buy_signal"] = False
    df["sell_signal"] = False

    df["crossover"] = df["MACD_line"] - df["signal_line"]

    df.loc[(df["crossover"] > 0) & (df["crossover"].shift(1) <= 0), "buy_signal"] = True

    df.loc[(df["crossover"] < 0) & (df["crossover"].shift(1) >= 0), "sell_signal"] = True

    balance = 1000
    position = None

    for index, row in df.iterrows():
        #Buy condition
        if position is None and row["buy_signal"] is True:
            buy_price = row["close"]
            pos_size = balance
            position = {
                "buy_price": buy_price,
                "pos_size": pos_size,
            }
            #print(f"{index} - Buy BTC for {pos_size}$ at {buy_price}$")
    
        elif position is not None and row["sell_signal"] is True:
            sell_price = row["close"]
            trade_result = (sell_price - position["buy_price"]) / position["buy_price"]
            balance = balance + trade_result * position["pos_size"]
            #print(f"{index} - Sell BTC for {balance}$ at {sell_price}$ ({round(trade_result * 100, 2)} %)")
            position = None
        
 

    print(f"{round((((balance / 1000) - 1) * 100), 2)} %")
