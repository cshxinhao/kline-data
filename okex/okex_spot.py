import requests
import logging
import pandas as pd
from datetime import datetime, timedelta
import time
import dateutil.parser
from sqlalchemy import create_engine

creds = {'usr': 'ONEBIT',
         'pwd': 'mafmmafm2020',
         'hst': '127.0.0.1',
         'prt': 3306,
         'dbn': 'crypto_data'}

conn = create_engine('mysql+pymysql://{usr}:{pwd}@{hst}:{prt}/{dbn}'.format(**creds))

quotes = ['USDT', 'USD']
bases = ['BTC', 'ETH', 'LTC', 'ETC', 'XRP', 'EOS', 'BCH', 'BSV', 'TRX']


class OKEX_SPOT_MD:

    def __init__(self, start_time: datetime, end_time: datetime, size: int):
        """start_time > end_time"""
        """size<=300"""
        self.session = requests.session()
        self.url = "https://www.okex.com"

        self.logger = logging.getLogger()
        self.logger.setLevel(logging.INFO)
        formatter = logging.Formatter("%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s")
        fh = logging.FileHandler('okex_spot_md.log', mode='a')
        fh.setFormatter(formatter)
        self.logger.addHandler(fh)
        self.start_datetime = datetime.strftime(start_time, "%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
        self.end_datetime = datetime.strftime(end_time, "%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
        self.size = size

    def get_instruments(self):
        data = self.session.get(self.url + '/api/spot/v3/instruments').json()
        # return [[item['instrument_id'], item['base_currency'], item['quote_currency']] for item in data if
        #         (item['base_currency'] in bases)]
        return [[item['instrument_id'], item['base_currency'], item['quote_currency']] for item in data if
                (item['base_currency'] in bases and item['quote_currency'] in quotes)]


    def __get_kline_by_instrument(self, instrument_name: str, start_datetime: str, end_datetime: str, freq,
                                  base_currency, quote_currency):
        try:
            data = self.session.get(
                self.url + '/api/spot/v3/instruments/{}/history/candles?start={}&end={}&granularity={}&limit={}'.format(
                    instrument_name,
                    start_datetime,
                    end_datetime,
                    str(freq),
                    self.size)).json()
            data = pd.DataFrame(data)
            if len(data.index) > 0:
                new_col = ['start_datetime', 'open', 'high', 'low', 'close', 'volume']
                data.columns = new_col
                data['start_datetime'] = data['start_datetime'].apply(
                    lambda x: (time.mktime(dateutil.parser.parse(x).timetuple()) * 1e3 + dateutil.parser.parse(
                        x).microsecond / 1e3) / 1e3)
                data['global_symbol'] = 'SPOT-{}/{}'.format(base_currency.upper(), quote_currency.upper())
                data['freq_seconds'] = freq
                self.logger.info("Successfully fetched {} kline @ {}".format(instrument_name, str(self.start_datetime)))
                return data
            else:
                self.logger.error("None data returned.")
                self.logger.error("None data returned for {} kline @ {}".format(instrument_name, str(
                    self.start_datetime)))
                return None
        except Exception as e:
            self.logger.error(
                self.url + '/api/spot/v3/instruments/{}/history/candles?start={}&end={}&granularity={}&limit={}'.format(
                    instrument_name,
                    start_datetime,
                    end_datetime,
                    str(freq),
                    self.size))

    def get_klines(self, freq: int):
        """freq must in [60/180/300/900/1800/3600/7200/14400/21600/43200/86400/604800]"""
        instruments = self.get_instruments()
        for instrument in instruments:
            kline_frame = self.__get_kline_by_instrument(instrument_name=instrument[0],
                                                         start_datetime=self.start_datetime,
                                                         end_datetime=self.end_datetime, freq=freq,
                                                         base_currency=instrument[1],
                                                         quote_currency=instrument[2])
            if kline_frame is not None:
                kline_frame.to_sql(name='OKEX_SPOT_OFFICIAL_KLINES', con=conn, if_exists='append', method='multi', index=False)
            time.sleep(0.1)


if __name__ == "__main__":
    okex_spot = OKEX_SPOT_MD(start_time=datetime.now(), end_time=datetime.now(), size=300)
    #print(okex_spot.get_instruments())
    start = datetime(2020, 9, 18)
    while start > datetime(2019, 1, 1):
        print(start)
        end = max(start - timedelta(minutes=300), datetime(2019, 1, 1))
        okex_spot.start_datetime = datetime.strftime(start, "%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
        okex_spot.end_datetime = datetime.strftime(end, "%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
        okex_spot.get_klines(freq=60)
        start = end