import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import torch
from torch import nn
from torch.utils.data import Dataset, DataLoader
import numpy as np
import openpyxl
import time


def load_avg_balances_csv(filepath='bse_d001_i10_0001_avg_balance.csv'):

    # Don't use any column as index
    df = pd.read_csv(filepath, header=None, index_col=None)

    df.replace(r'^\s*$', np.nan, regex=True, inplace=True)
    df.dropna(axis=1, how='any', inplace=True)

    base_cols = ['session_id', 'time', 'best_bid', 'best_ask']

    # Dynamically label the trader columns
    num_extra_cols = df.shape[1] - 4
    num_trader_types = num_extra_cols // 4

    trader_cols = []
    for i in range(num_trader_types):
        trader_cols += [
            f'trader_type_{i+1}',
            f'total_profit_{i+1}',
            f'trader_count_{i+1}',
            f'avg_profit_{i+1}'
        ]

    df.columns = base_cols + trader_cols    
    print(df.columns)

    return df, num_trader_types


def load_tape(filename='/Users/keeganhill/Documents/ALGO/BristolStockExchange-master/bse_d001_i10_0001_tape.csv'):

    target_previous = {}
    df = pd.read_csv(filename, header=None)
    df.columns = ['Type', 'Time', 'Price']

    df.drop('Type', axis=1, inplace=True)

    previous_samples = 3

    for i in range(previous_samples, len(df)):
        previous_prices = []
        target, timestamp = df['Price'].iloc[i],df['Time'].iloc[i]
        previous_prices.append(target)

        for j in range(1, previous_samples + 1):
            previous_prices.append(df['Price'].iloc[i - j])

        previous_prices = list(reversed(previous_prices))
        target_previous[timestamp] = previous_prices

    df_windowed = pd.DataFrame.from_dict(target_previous, orient='index')

    columns = [f'feature_{x}' for x in range(1, len(list(target_previous.values())[0]))]
    columns.append('target_price')

    df_windowed.columns = columns
    # Optional: Reset index name
    df_windowed.index.name = 'time_step'

    print(df)
    plt.plot(df['Price'])
    plt.show()

    # uncomment to save file
    # df_windowed.to_excel('LSTM_input.xlsx')


if __name__ == "__main__":

    load_avg_balances_csv()

    '''df, num_trader_types = load_avg_balances_csv()

    for i in range(1, num_trader_types + 1):

        trader_name = df[f'trader_type_{i}'].unique()[0]
        plt.plot(df[f'avg_profit_{i}'], label=trader_name)

    plt.legend()
    plt.show()'''
