#!/usr/bin/env python
# -*- coding:utf-8 -*-
# author linfeng
import base64
import json
import time
import requests
import csv
import random
import hashlib
try:
    from urllib import urlencode
except ImportError:
    from urllib.parse import urlencode

ENDPOINT = "https://api.bit-z.com/api_v1/"

def formatNumber(x):
    if isinstance(x, float):
        return "{:.8f}".format(x)
    else:
        return str(x)


class BitClient():
    def __init__(self,apikey,secretkey,tradepwd):
        self._public_key = apikey
        self._private_key = secretkey
        self._trade_pwd = tradepwd
        self.session = requests.session()
        self.session.keep_alive = False
        self.adapter = requests.adapters.HTTPAdapter(pool_connections=1,
                                                     pool_maxsize=5, max_retries=5)
        self.session.mount('http://', self.adapter)
        self.session.mount('https://', self.adapter)
        
        self._exchange_name = 'bit-z'
        self.rebalance = 'off'
        self.Slippage = 0.002  # 滑点
    
    def signature(self,message):
        print('signature')
        content = message + self._private_key
        signature = hashlib.md5(content.encode('utf-8')).hexdigest().lower()
     
        return signature
    
    def signedRequest(self, method, path, params:dict):

        _timestamp = str(int(time.time()))
        _nonce = str(random.randint(100000,999999))
        params['timestamp'] = _timestamp
        params['nonce'] = _nonce
        params['api_key'] = self._public_key
        param = ''

        for key in sorted(params.keys()):
            param += key + '=' + str(params.get(key)) + '&'
        param = param.rstrip(' & ')
       
        signature = self.signature(message=param)
     
        params['sign'] = str(signature)
        print(params)
        resp = self.session.request(method,ENDPOINT + path,headers=None,data=None,params=params)
    
        data = json.loads(resp.content)
        return data
    
    def ticker(self,symbol):
        params = {'coin':symbol}
        data = self.signedRequest(method="GET",path = 'ticker',params=params)['data']
        return data

    def depth(self,symbol):
        '''
        显示深度10档的信息
        '''
        symbol = symbol.lower()
        params = {'coin': symbol}
        data = self.signedRequest(method='GET',path = 'depth',params=params)['data']
        temp = {'asks':data['asks'][:10],'bids':data['bids'][:10]}
        return temp
    
    def balance(self):
        """Get current balances for all symbols.
        只有全部的余额情况，没有冻结资金与可用资金的区分。
        """
        params = {}
        try:

            data = self.signedRequest(method="POST", path= "balances",params=params)['data']
            data.pop('uid')
            new_data = {'asset':data}
            return new_data
        except Exception as e:
            return e
    def trade(self,type,amount,price,symbol):   #只有限价买卖的功能
        """
        委托下单 tradeAdd
        访问方式 POST
        参数
        字段	说明
        symbol	交易对符号，例如：ltc_btc
        type	buy / 买，sell / 卖
        price	委托价格
        number	委托数量
        tradepwd 交易密码
        返回
        字段	说明
        code        状态码
        msg      	success or fail reason
        data        order_id
        """
        symbol = symbol.lower()
        if type == 'buy':
            type = 'in'
        if type == 'sell':
            type = 'out'
        params = {
            "type": str(type),
            "coin": symbol,
            "price": float(price),
            "number": float(amount),
            "tradepwd":str(self._trade_pwd)
        }
        data = self.signedRequest("POST", path = "tradeAdd", params=params)['data']

        return data

    def cancel(self, order_id,symbol=None, **kwargs):
        params = {'id': order_id}
        params.update(kwargs)
        data = self.signedRequest("POST", path='tradeCancel', params=params)
        return data

    def openOrders(self,symbol,order_id=None,**kwargs):
        symbol = symbol.lower()
        params = {'coin':symbol}
        #params.update(kwargs)
        data = self.signedRequest(method="POST", path="openOrders", params=params)['data']
        return data
    
    def cancel_all(self,order_id_list=None,symbol='mzc_btc'):   #没有具体调整
        symbol = symbol.lower()
        if order_id_list:
            for i in order_id_list:
                try:
                    result = self.cancel(order_id=i,symbol=symbol)
                except:
                    continue
        else:
            order_id_list=[]
            openorders = self.openOrders(symbol)
            for i in openorders:
                if type(i) == type({}):
                    order_id_list.append(i['orderId'])
                    print(order_id_list)
            for i in order_id_list:
                try:
                    result = self.cancel(order_id=i,symbol=symbol)
                    print(result)
                except:
                    continue



