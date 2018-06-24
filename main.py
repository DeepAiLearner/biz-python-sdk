import config
from bitz import BitClient
import time
from threading import Thread

class app():
    def __init__(self):
        self.bitCoin = BitClient(config.API_KEY,config.API_SECRET,config.TRADE_PWD)
        self.symbol = config.symbol

    def process(self):
        self.bitCoin.ticker('mzc_btc')
        self.bitCoin.depth('mzc_btc')
        self.bitCoin.balance()
    
    def loop(self):
        print('开始买卖')
        while True:
            try:
                self.process()
            except Exception as err:
                print (err)
            time.sleep(4)
    

if __name__ == '__main__':
    run = app()
    thread = Thread(target=run.loop)
    thread.start()
    thread.join()