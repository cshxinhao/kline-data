import requests
import logging
import pandas as pd 
from datetime import datetime 

class Binance_SWAP_MD:
    def __init__(self, start_time: datetime, end_time: datetime):
        self.url = "https://fapi.binance.com"
        self.start_datetime = start_time.timestamp()
        self.end_datetime = end_time.timestamp()
        self.session = requests.session()

        # initilize the logger
        self.logger = logging.getLogger()
        self.logger.setLevel(logging.INFO)
        formatter = logging.Formatter("%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s")
        fh = logging.FileHandler('binance_swap_MD.log', mode='a')
        fh.setFormatter(formatter)
        self.logger.addHandler(fh)
    
        self.__freq_mapping = {
            '60': '1m',
            '180': '3m',
            '300': '5m',
            '900': '15m',
            '1800': '30m',
            '3600': '1h',
            '14400': '4h',
            '86400': '1d'
        }
    

    def get_instruments(self):
        data = self.session.get(self.url + '/fapi/v1/exchangeInfo').json()
        return [item['symbol'] for item in data['symbols']]
    
    def __get_kline_by_instrument(self, instrument_name, start_datetime, end_datetime, freq):
        data = self.session.get(self.url + "/fapi/v1/klines?symbol={}&interval={}&limit=1500".format(
            instrument_name, self.__freq_mapping[str(freq)], 10*int(self.start_datetime), 10*int(self.end_datetime)
        )).json()
        data = pd.DataFrame(data, columns = ['Open time', 'open', 'high', 'low', "close", 'volume', 'close time', 'amount', 'trades', 'taker base', 'taker quote', 'ignore'])
        if len(data.index) > 0:
            data['start_datetime'] = data['Open time'].apply(lambda x: x//1000)
            data = data[['open', 'high', 'low', 'close', 'volume', 'amount', 'start_datetime']]
            data['freq_seconds'] = freq
            data['global_symbol'] = 'SWAP-{}/USDT'.format(instrument_name.split('USDT')[0])
            self.logger.info("Succesfully fetched {} kline @ {}".format(instrument_name, str(datetime.fromtimestamp(self.start_datetime))))
            return data
        else:
            self.logger.error("Failed to fetched {} kline @ {}".format(instrument_name, str(datetime.fromtimestamp(self.start_datetime))))
            return None

    def get_klines(self, freq):
        instruments = self.get_instruments()
        for instrument in instruments:
            data = self.__get_kline_by_instrument(instrument_name=instrument, start_datetime=self.start_datetime, end_datetime=self.end_datetime, freq=freq)
            if data is not None:
                data.to_csv('test.csv')

if __name__ == "__main__":
    binance_swap_md = Binance_SWAP_MD(start_time=datetime(2020,9,2), end_time=datetime(2020,9,3))
    binance_swap_md.get_klines(freq=60)