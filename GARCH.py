import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import math

data = pd.read_csv(rf'C:\Users\Romain\Desktop\Trade\Codes\Databases Training\GOLD\XAU_1D.csv')
data.columns = ['date', 'time', 'open', 'high', 'low', 'close', 'volume']
del data['time']
del data['volume']
data['date'] = pd.to_datetime(data['date'], format="%Y.%m.%d")
#data['ohlc4'] = (data['open'] + data['high'] + data['low'] + data['close']) / 4 
data = data[data['date'].dt.year >= 2021]
data = data.set_index(['date'])

#####

data['returns'] = data['close'] / data['close'].shift(1) - 1

mean_returns = data['returns'].mean()
std_returns = data['returns'].std()
var_returns = std_returns**2

u = mean_returns
w = var_returns
a = 0
b = 0

data['epsilon'] = data['returns'] - u
data['epsilon_t-1**2'] = data['epsilon'].shift(1)**2
data['epsilon_t-1**2'] = data['epsilon_t-1**2'].fillna(0)
data['var_cond'] = w + a*data['epsilon_t-1**2']

data['L'] = (1/(2 * math.pi * data['var_cond'])**(-2)) *  math.e ** (-((data['epsilon'] ** 2)/(2*data['var_cond'])))
data['Log_L'] = np.log10(data['L'])
data['LLH_sum'] = data['Log_L'].cumsum()
data