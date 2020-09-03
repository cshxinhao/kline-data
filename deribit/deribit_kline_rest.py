import requests
import pandas as pd
from datetime import datetime
import logging


class Deribit_MD:

    def __init__(self, start_time: datetime, end_time:datetime):
        self.session = requests.session()
        self.__freq_map = {
            '60': '1',
            '180': '3',
            '300': '5',
            '600': '10',
            '900': '15',
            '1800': '30',
            '3600': '60',
            '86400': '1D'
        }
        self.logger = logging.getLogger()
        self.logger.setLevel(logging.INFO)
        formatter = logging.Formatter("%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s")
        fh = logging.FileHandler('deribit_marketData.log', mode='a')
        fh.setFormatter(formatter)
        self.logger.addHandler(fh)
        self.start_datetime = start_time.timestamp()
        self.end_datetime = end_time.timestamp()


    @staticmethod
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

    def __get_instrument_name(self):
        data = self.session.get("https://www.deribit.com/api/v2/public/get_book_summary_by_currency?currency=BTC")
        data = data.json()
        self.instruments = [d['instrument_name'] for d in data['result']]

    def __get_kline_by_instrument(self, instrument_name: str, start_datetime: datetime.timestamp, end_datetime: datetime.timestamp, freq: int):
        data = self.session.get("https://www.deribit.com/api/v2/public/get_tradingview_chart_data?instrument_name={}&resolution={}&start_timestamp={}&end_timestamp={}".format(instrument_name, self.__freq_map[str(freq)], int(start_datetime)* 1000, int(end_datetime) * 1000)).json()['result']
        data['amount'] = data.pop('cost')
        data['start_datetime'] = data.pop('ticks')
        data = pd.DataFrame(data=data)
        if len(data.index) > 0:
            del data['status']
            data['start_datetime'] = data['start_datetime'].apply(lambda x: int(x) // 1000 - 3600 * 8)
            data['frequency'] = freq
            data['global_symbol'] = Deribit_MD.get_global_symbol(exchange_symbol=instrument_name)
            return data
        else:
            return None
    
    def get_klines(self, freq: int):
        self.__get_instrument_name()
        for instrument in self.instruments:
            kline_frame = self.__get_kline_by_instrument(instrument_name=instrument, start_datetime=self.start_datetime, end_datetime=self.end_datetime, freq=60)
            if kline_frame is None:
                self.logger.error("{} kline frame @ {} returned no data".format(instrument, str(datetime.fromtimestamp(self.start_datetime - 8 * 3600))))
            else:
                kline_frame.to_csv('deribit_kline_frame/{}.csv'.format(instrument + str(int(self.start_datetime))))
                self.logger.info("Succesfully fetched {} kline frame @ {}".format(instrument, str(datetime.fromtimestamp(self.start_datetime - 8 * 3600))))


if __name__ == "__main__":
    deribit = Deribit_MD(start_time=datetime(2020,9,1,8), end_time=datetime(2020,9,3,8))
    deribit.get_klines(freq = 60)