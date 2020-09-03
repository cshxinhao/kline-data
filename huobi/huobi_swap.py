import requests
import logging
import pandas as pd 
from datetime import datetime

class Huobi_SWAP_MD:

    def __init__(self, start_time: datetime, end_time: datetime):
        self.session = requests.session()
        self.url = "https://api.hbdm.com"
        self.start_datetime = start_time.timestamp()
        self.end_time = end_time.timestamp()

        self.logger = logging.getLogger()
        self.logger.setLevel(logging.INFO)
        formatter = logging.Formatter("%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s")
        fh = logging.FileHandler('huobi_swap_md.log', mode='a')
        fh.setFormatter(formatter)
        self.logger.addHandler(fh)
        self.start_datetime = int(start_time.timestamp())
        self.end_datetime = int(end_time.timestamp())

        self.__freq_map = {
            '60': '1min',
            '300': '5min',
            '900': '15min',
            '1800': '30min',
            '3600': '60min',
            '14400': '4hour',
            '86400': '1day'
        }
    
    def get_instruments(self):
        data = self.session.get(self.url + '/swap-api/v1/swap_contract_info').json()
        return [d['contract_code'] for d in data['data']]
    
    def __get_kline_by_instrument(self, instrument_name: str, start_datetime: int, end_datetime: int, freq):
        data = self.session.get(self.url + '/swap-ex/market/history/kline?contract_code={}&period={}&from={}&to={}'.format(instrument_name, self.__freq_map[str(freq)], self.start_datetime, self.end_datetime)).json()['data']
        data = pd.DataFrame(data)
        if len(data.index) > 0:
            data = data.rename(columns={"id": 'start_datetime'})
            data['start_datetime'] = data['start_datetime'].apply(lambda x: datetime.fromtimestamp(x))
            data['global_symbol'] = 'SWAP-{}'.format(instrument_name.replace('-', '/'))
            data['freq_seconds'] = freq
            self.logger.info("Successfully fetched {} kline @ {}".format(instrument_name, str(datetime.fromtimestamp(self.start_datetime))))
            return data
        else:
            self.logger.error("None data returned.")
            self.logger.error("None data returned for {} kline @ {}".format(instrument_name, str(datetime.fromtimestamp(self.start_datetime))))
            return None
    
    def get_klines(self, freq: int):
        instruments = self.get_instruments()
        for instrument in instruments:
            kline_frame = self.__get_kline_by_instrument(instrument_name=instrument, start_datetime=self.start_datetime, end_datetime = self.end_datetime, freq=freq)
            if kline_frame is not None:
                kline_frame.to_csv("example.csv")


if __name__ == "__main__":
    huobi = Huobi_SWAP_MD(datetime(2020, 9, 2), datetime(2020, 9, 3))
    huobi.get_klines(freq=60)