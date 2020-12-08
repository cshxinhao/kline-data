from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import pandas as pd

creds = {'usr': 'trader',
         'pwd': 'mafmmafm2020',
         'hst': '127.0.0.1',
         'prt': 3306,
         'dbn': 'crypto_data'}

conn = create_engine('mysql+pymysql://{usr}:{pwd}@{hst}:{prt}/{dbn}'.format(**creds))

def fetch_klines(table: str, instrument: str, start_datetime: datetime, end_datetime: datetime)->pd.DataFrame:
    Session = sessionmaker(bind=conn)
    start = int(start_datetime.timestamp())
    end = int(end_datetime.timestamp())
    session = Session()
    data = []
    result = session.execute("SELECT open, high, low, close, volume, amount, start_datetime from {}_OFFICIAL_KLINES where start_datetime>={} and start_datetime<={} and global_symbol='{}'".format(table, start, end, instrument))
    for row in result:
        data.append(row)
    session.close()
    data = pd.DataFrame(data=data, columns=['open', 'high', 'low', 'close', 'volume', 'amount', 'start_datetime'])
    return data

if __name__ == "__main__":
    df = fetch_klines("BINANCE_SWAP", instrument='SWAP-BTC/USDT', start_datetime=datetime(2020,1,1), end_datetime=datetime(2020,6,30))
    df.to_csv("havealook.csv")