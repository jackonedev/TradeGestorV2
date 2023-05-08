import numpy as np
import pandas as pd

def true_range(df):
    df['tr0'] = abs(df["high"] - df["low"])
    df['tr1'] = abs(df["high"] - df["close"].shift())
    df['tr2'] = abs(df["low"] - df["close"].shift())
    df['tr'] = df[['tr0', 'tr1', 'tr2']].max(axis=1)
    df.drop(['tr0', 'tr1', 'tr2'], axis=1, inplace=True)
    return df['tr']

def squeeze_momentum_indicator(data, length=20, mult=2, length_KC=20, mult_KC=1.5, use_EMA=True):

    # calculate BB
    m_avg = data['close'].rolling(window=length).mean()
    m_std = data['close'].rolling(window=length).std(ddof=0)
    data['upper_BB'] = m_avg + mult * m_std
    data['lower_BB'] = m_avg - mult * m_std

    # calculate true range
    data['tr'] = true_range(data)

    # calculate KC
    if use_EMA:
        atr = data['tr'].ewm(span=length_KC, adjust=False).mean()
    else:
        atr = data['tr'].rolling(window=length_KC).mean()
    data['upper_KC'] = m_avg + atr * mult_KC
    data['lower_KC'] = m_avg - atr * mult_KC

    # calculate bar value
    highest = data['high'].rolling(window = length_KC).max()
    lowest = data['low'].rolling(window = length_KC).min()
    m1 = (highest + lowest)/2
    data['value'] = (data['close'] - (m1 + m_avg)/2)
    fit_y = np.array(range(0,length_KC))
    data['value'] = data['value'].rolling(window = length_KC).apply(lambda x: 
                            np.polyfit(fit_y, x, 1)[0] * (length_KC-1) + 
                            np.polyfit(fit_y, x, 1)[1], raw=True)

    # check for 'squeeze'
    def in_squeeze(data):
            return data['lower_BB'] > data['lower_KC'] and data['upper_BB'] < data['upper_KC']
    data['squeeze_on'] = data.apply(in_squeeze, axis=1)

    return data

def check_entry(data):
    """Returns 1 if we should enter long, -1 if we should enter short, or 0 if we should stay out of the market"""
    # buying window for long position:
    # 1. black cross becomes gray (the squeeze is released)
    squeeze_released = (data.iloc[-2]['squeeze_on']) & (not data.iloc[-1]['squeeze_on'])
    # 2. bar value is positive => the bar is light green k
    long_cond = data['value'][-1] > 0
    enter_long = squeeze_released and long_cond

    # buying window for short position:
    # 1. black cross becomes gray (the squeeze is released)
    # 2. bar value is negative => the bar is light red 
    short_cond = data['value'][-1] < 0
    enter_short = squeeze_released and short_cond
    if enter_long:
        return 1
    elif enter_short:
        return -1
    else:
        return 0


def backtest_entry(data):
    """Return dataframe with entry points marked"""
    # Lista para almacenar los índices de las filas que cumplen las condiciones
    buy_long_indices = []
    buy_short_indices = []

    # Iterar a través de todas las filas del dataframe
    for i in range(len(data)):
        # Verificar si se cumple la condición para una posición larga
        squeeze_released = (data.iloc[i-1]['squeeze_on']) & (not data.iloc[i]['squeeze_on'])
        long_cond = data['value'][i] > 0#TODO: MÁS QUE MAYOR A CERO, QUE TENGA PENDIENTE POSITIVA
        # long_cond = data['value'][i] < 0 and data['value'][i] > data['value'][i-1]#TODO: nueva versión
        if squeeze_released and long_cond:#TODO: cambiado a or
            buy_long_indices.append(i)
            
        # Verificar si se cumple la condición para una posición corta
        short_cond = data['value'][i] < 0
        if squeeze_released and short_cond:
            buy_short_indices.append(i)

    df_short = data.iloc[buy_short_indices]
    df_short.name = 'short'
    df_long = data.iloc[buy_long_indices]
    df_long.name = 'long'
    return df_short, df_long