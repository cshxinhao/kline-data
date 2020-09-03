import requests
import pandas as pd
from datetime import datetime

session = requests.session()

freq_map = {
    '60': '1',
    '180': '3',
    '300': '5',
    '600': '10',
    '900': '15',
    '1800': '30',
    '3600': '60',
    '86400': '1D'
}

def get_global_symbol(exchange_symbol):
    if len(exchange_symbol.split('-')) > 2:
        split_list = exchange_symbol.split('-')
        asset = split_list[0]
        time = datetime.strptime(split_list[1], '%d%b%y').strftime('%Y%m%d')
        strike = split_list[2]
        option_type = split_list[3]
        return "OPT-{}-{}-{}-{}".format(asset, time, strike, option_type)
    else:
        if exchange_symbol == 'BTC-PERPETUAL':
            return "SWAP-BTC/USD"
        else:
            split_list = exchange_symbol.split('-')
            symbol = split_list[0]
            time = datetime.strptime(split_list[1], '%d%b%y').strftime('%Y%m%d')
            return "FUTU-{}-{}".format(symbol, time)

def get_instrument_name():
    data = session.get("https://www.deribit.com/api/v2/public/get_book_summary_by_currency?currency=BTC")
    data = data.json()
    return [d['instrument_name'] for d in data['result']]

def get_deribit_kline(instrument_name: str, start_datetime: datetime.timestamp, end_datetime: datetime.timestamp, freq: int):
    data = session.get("https://www.deribit.com/api/v2/public/get_tradingview_chart_data?instrument_name={}&resolution={}&start_timestamp={}&end_timestamp={}".format(instrument_name, freq_map[str(freq)], int(start_datetime)* 1000, int(end_datetime) * 1000)).json()['result']
    data['amount'] = data.pop('cost')
    data['start_datetime'] = data.pop('ticks')
    data = pd.DataFrame(data=data)
    del data['status']
    data['start_datetime'] = data['start_datetime'].apply(lambda x: int(x) // 1000 - 3600 * 8)
    data['frequency'] = freq
    data['global_symbol'] = get_global_symbol(exchange_symbol=instrument_name)
    #data['start_datetime'] = data['start_datetime'].apply(lambda x: str(datetime.fromtimestamp(x)))
    #print(data)
    return data

if __name__ == "__main__":
    
    get_deribit_kline(instrument_name='BTC-25DEC20-14000-C', start_datetime = datetime(2020,9,2,0).timestamp(), end_datetime=datetime(2020,9,3,8,12).timestamp(), freq=60)