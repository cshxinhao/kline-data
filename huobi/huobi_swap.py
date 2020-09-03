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
        self.start_datetime = start_time.timestamp()
        self.end_datetime = end_time.timestamp()
    

