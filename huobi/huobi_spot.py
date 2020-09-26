import websocket
import json
from datetime import datetime, timedelta
import requests
import gzip
import _thread as thread
import time
import pandas as pd
from sqlalchemy import create_engine

creds = {'usr': 'ONEBIT',
         'pwd': 'mafmmafm2020',
         'hst': '127.0.0.1',
         'prt': 3306,
         'dbn': 'crypto_data'}

conn = create_engine('mysql+pymysql://{usr}:{pwd}@{hst}:{prt}/{dbn}'.format(**creds))

quotes = ['usdt', 'usdc']
bases = ['btc', 'eth']

start_datetime = datetime(2019,1,1,0)
end_datetime = datetime(2019,1,1,5)
benchmark = datetime(2020,9,18)

def get_instruments():
    data = requests.get("https://api.huobi.pro/v1/common/symbols").json()
    return [[item['base-currency'], item['quote-currency']] for item in data['data']]

class Huobi_MD(object):
    def __init__(self, start_datetime: datetime, end_datetime: datetime):
        websocket.enableTrace(True)
        self.start_datetime = int(start_datetime.timestamp())
        self.end_datetime = int(end_datetime.timestamp())

    @staticmethod
    def on_message(ws, message):
        data = json.loads(gzip.decompress(message).decode())
        if "ping" in data:
            ws.send(json.dumps({"pong": int(datetime.now().timestamp() * 1000)}))
        elif "data" in data:
            df = pd.DataFrame(data["data"])
            #df.to_csv('example.csv')
            df['start_datetime'] = df['id']
            df['volume'] = df['vol']

            del df['id']
            del df['vol']
            del df['count']

            df['freq_seconds'] = 60
            df['global_symbol'] = "SPOT-{}".format(data['id'].upper())
            df = df[df['start_datetime'] < end_datetime.timestamp()]
            df.to_sql(name='HUOBI_SPOT_OFFICIAL_KLINES', con=conn, if_exists='append', method='multi',index=False)
            #print(df)

    @staticmethod
    def on_error(ws, error):
        print(error)

    @staticmethod
    def on_close(ws):
        print("Connection closed...")

    @staticmethod
    def on_open(ws):
        def run(*args):
            global start_datetime, end_datetime
            instruments = get_instruments()
            #instruments = [['btc', 'usdt'], ['eth', 'usdt']]
            while(end_datetime < benchmark):
                print(start_datetime)
                for instrument in instruments:
                    symbol = instrument[0] + instrument[1]
                    req = {
                        "req": "market.{}.kline.1min".format(symbol),
                        "id": "{}/{}".format(instrument[0], instrument[1]),
                        "from": int(start_datetime.timestamp()),
                        "to": int(end_datetime.timestamp())
                    }
                    time.sleep(0.5)
                    ws.send(json.dumps(req))
                start_datetime = end_datetime
                end_datetime = min(end_datetime + timedelta(hours=5), benchmark)
        thread.start_new_thread(run, ())



if __name__ == "__main__":
    #huobi_md = Huobi_MD(datetime(2019,1,1), datetime(2019,1,1,5))
    ws = websocket.WebSocketApp(url='wss://api.huobi.pro/ws',
                                on_close=Huobi_MD.on_close,
                                on_error=Huobi_MD.on_error,
                                on_message=Huobi_MD.on_message,
    )
    ws.on_open = Huobi_MD.on_open
    ws.run_forever(ping_timeout=30)