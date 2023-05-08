import pandas as pd

def response_to_dataframe(response):
    data = response['data']
    if len(data) == 0:
        return
    df = pd.DataFrame(data)
    df['time'] = pd.to_datetime(df['time'], unit='ms')
    df[['open', 'close', 'high', 'low', 'volume']] = df[['open', 'close', 'high', 'low', 'volume']].astype(float)
    return df