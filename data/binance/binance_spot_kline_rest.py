import requests
import logging
import pandas as pd
from datetime import datetime, timedelta
import time
from sqlalchemy import create_engine

creds = {'usr': 'ONEBIT',
         'pwd': 'mafmmafm2020',
         'hst': '127.0.0.1',
         'prt': 3306,
         'dbn': 'crypto_data'}

conn = create_engine('mysql+pymysql://{usr}:{pwd}@{hst}:{prt}/{dbn}'.format(**creds))

quotes = ['USDT', 'USDC']
bases = ['BTC', 'ETH']

class Binance_SPOT_MD:
    def __init__(self, start_time: datetime, end_time: datetime):
        self.url = "https://api.binance.com"
        self.start_datetime = start_time.timestamp()
        self.end_datetime = end_time.timestamp()
        self.session = requests.session()

        # initilize the logger
        self.logger = logging.getLogger()
        self.logger.setLevel(logging.INFO)
        formatter = logging.Formatter("%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s")
        fh = logging.FileHandler('binance_spot_MD.log', mode='a')
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
        data = self.session.get(self.url + '/api/v3/exchangeInfo').json()
        return [[item['symbol'], item['baseAsset'], item['quoteAsset'] ] for item in data['symbols'] if (item['baseAsset'] in bases or item['quoteAsset'] in quotes)]

    def __get_kline_by_instrument(self, instrument_name, start_datetime, end_datetime, freq, baseAsset, quoteAsset):
        data = self.session.get(self.url + "/api/v3/klines?symbol={}&interval={}&limit=1500&startTime={}&endTime={}".format(
            instrument_name, self.__freq_mapping[str(freq)], 1000 * int(start_datetime), 1000 * int(end_datetime)
        )).json()
        data = pd.DataFrame(data,
                            columns=['Open time', 'open', 'high', 'low', "close", 'volume', 'close time', 'amount',
                                     'trades', 'taker base', 'taker quote', 'ignore'])
        if len(data.index) > 0:
            data['start_datetime'] = data['Open time'].apply(lambda x: x // 1000)
            data = data[['open', 'high', 'low', 'close', 'volume', 'amount', 'start_datetime']]
            data['freq_seconds'] = freq
            data['global_symbol'] = 'SPOT-{}/{}'.format(baseAsset,quoteAsset)
            self.logger.info("Succesfully fetched {} kline @ {}".format(instrument_name, str(
                datetime.fromtimestamp(self.start_datetime))))
            return data
        else:
            self.logger.error("Failed to fetched {} kline @ {}".format(instrument_name, str(
                datetime.fromtimestamp(self.start_datetime))))
            return None

    def get_klines(self, freq):
        instruments = self.get_instruments()
        #instruments = [['BTCUSDT', 'BTC', 'USDT']]
        for instrument in instruments:
            data = self.__get_kline_by_instrument(instrument_name=instrument[0], start_datetime=self.start_datetime,
                                                  end_datetime=self.end_datetime, freq=freq, baseAsset=instrument[1],
                                                  quoteAsset=instrument[2])
            if data is not None:
                #data.to_csv('test.csv')
                #print(data['start_datetime'])
                data = data[data['start_datetime'] < self.end_datetime]
                data.to_sql(name='BINANCE_SPOT_OFFICIAL_KLINES', index=False, if_exists='append', con=conn, method='multi')
                time.sleep(0.1)


if __name__ == "__main__":
    binance_spot = Binance_SPOT_MD(start_time=datetime.now(), end_time=datetime.now())
    start = datetime(2019, 1, 1, 0)
    while start < datetime(2020, 9, 18):
        print(start)
        end = min(start + timedelta(minutes=1000), datetime(2020, 9, 18))
        binance_spot.start_datetime = start.timestamp()
        binance_spot.end_datetime = end.timestamp()
        binance_spot.get_klines(freq=60)
        start = end