data = pd.read_csv('USDJPY_M15.csv')
data.columns = ['date', 'open', 'high', 'low', 'close', 'volume']
data['date'] = pd.to_datetime(data['date'])
data = data.set_index(['date'])
data['ohlc4'] = (data['open'] + data['high'] + data['low'] + data['close']) / 4 

######

in_pos = None
stop_loss = 0.005
rr = 4
strat_logs = []

for index, row in data.iterrows():
    if in_pos == 'long':
        if row.ohlc4 <= actual_stop:
            # Stop loss atteint
            exit_price = actual_stop
            exit_time = index
            pnl = exit_price - entry_price
            strat_logs.append([exit_price, entry_price, in_pos, entry_time, exit_time, pnl])
            in_pos = None
        elif row.ohlc4 >= take_profit:
            # Take profit atteint
            exit_price = take_profit
            exit_time = index
            pnl = exit_price - entry_price
            strat_logs.append([exit_price, entry_price, in_pos, entry_time, exit_time, pnl])
            in_pos = None
    elif in_pos == 'short':
        if row.ohlc4 >= actual_stop:
            # Stop loss atteint
            exit_price = actual_stop
            exit_time = index
            pnl = entry_price - exit_price
            strat_logs.append([exit_price, entry_price, in_pos, entry_time, exit_time, pnl])
            in_pos = None
        elif row.ohlc4 <= take_profit:
            # Take profit atteint
            exit_price = take_profit
            exit_time = index
            pnl = entry_price - exit_price
            strat_logs.append([exit_price, entry_price, in_pos, entry_time, exit_time, pnl])
            in_pos = None
    else:
        # Pas en position
        if row.ohlc4 > row.fvg_down and row.ohlc4 < row.fvg_up:
            if row.ohlc4 > row.buy_breaker_block_low and row.ohlc4 < row.buy_breaker_block_high:
                # Entrée en position longue
                in_pos = 'long'
                entry_price = row.ohlc4
                actual_stop = entry_price * (1 - stop_loss)
                stop_distance = entry_price - actual_stop
                take_profit = entry_price + stop_distance * rr
                entry_time = index
            elif row.ohlc4 > row.sell_breaker_block_low and row.ohlc4 < row.sell_breaker_block_high:
                # Entrée en position courte
                in_pos = 'short'
                entry_price = row.ohlc4
                actual_stop = entry_price * (1 + stop_loss)
                stop_distance = actual_stop - entry_price
                take_profit = entry_price - stop_distance * rr
                entry_time = index

strat_logs = pd.DataFrame(strat_logs, columns=['exit_price', 'entry_price', 'type', 'entry_time', 'exit_time', 'pnl'])

#####

plt.title("USDJPY / SL 0.5% / RR 4")
strat_logs['pnl'].cumsum().plot(figsize=(12,8))
plt.xlabel("Nombre de Trades")
plt.ylabel("PnL")
plt.savefig("USDJPY SL 0.5% RR 4.png")
plt.show()
