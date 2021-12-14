# While I have shown the power of using the RSI and MACD to predict short-term market trends in Bitcoin and the S&P 500,
# one of their major drawbacks is their lagging nature. Trends are only established after market moves, which means that
# these indicators will only give a buy signal after the price has already moved upwards and a sell signal after the price has
# already moved downwards considerably. This can commonly result in losses when the asset is trading within its Average True Range (ATR),
# which should be measured when the asset was purchased since the ATR will increase if the asset makes a major price move. To counter this, 
# we will store the ATR value when the asset was bought in a .txt file to be accessed by this algorithm. We will exit a profitable 
# position that has not been given a sell signal by the Moving Average Convergence Divergence (MACD) or Relative Strength Index (RSI),
# but has exceeded an RSI of 70, indicating that it is overbought, and is trading within its ATR. If the  asset is trading outside of 
# its ATR, this means that it is on a bull run, which can commonly drive prices upwards for an extended period of time even while the RSI remains above 70.

from twelvedata import TDClient 
from ibapi.client import EClient
from ibapi.contract import Contract
from ibapi.order import *
from ibapi.wrapper import EWrapper

from threading import Timer
import time
import pandas as pd

def runLoop(sample):
    sample.run()

class GetPositionApp(EWrapper, EClient): #Declare class and override methods that we will need, such as the error and order
    def __init__(self):
        EClient.__init__(self, self)

        self.allPositions = pd.DataFrame([], columns = ['Account','Symbol', 'Quantity', 'Average Cost', 'Sec Type'])
    def error(self, reqId, errorCode, errorString):
        print("Error: ", reqId, " ", errorCode, " ", errorString)
    
    def position(self, account: str, contract: Contract, position: float, avgCost: float):
        super().position(account, contract, position, avgCost)
        index = str(account)+str(contract.symbol)
        self.allPositions.loc[index]= account, contract.symbol, position, avgCost, contract.secType
    
    def positionEnd(self):
        super().positionEnd()
        self.disconnect()

def getPosition():
    positionApp = GetPositionApp() 
    positionApp.connect("127.0.0.1", 7496, 6)  # Should be a pause afterwards before invoking functions
    time.sleep(0.5) #Sleep interval to allow time for connection to server

    positionApp.reqPositions() # associated callback: position
    print("Waiting for IB's API response for accounts positions requests...\n")
    time.sleep(0.5)
    runLoop(positionApp)
    currentPositions = positionApp.allPositions
    currentPositions.set_index('Account',inplace=True,drop=True) #set all_positions DataFrame index to "Account"
    if(currentPositions.empty):
        return 0
    else:
        return currentPositions.iat[0,1] #return the quantity of stock currently held in account
position = getPosition()
signal = 0

td = TDClient(apikey='8600b4b5be4142e186c197b098338bbb')

rsi_ts = td.time_series(symbol='BTC/USD',interval='30min',outputsize=1,timezone='America/New_York')# The RSI value needs to be calculated in the same time interval as we are trading

indicators = rsi_ts.with_rsi().as_pandas()
rsi = indicators.iloc[0]['rsi']
    
price_ts = td.time_series(symbol='BTC/USD',interval='1min',outputsize=1,timezone='America/New_York') # 1 minute interval to get the most up-to-date price
prices = price_ts.as_pandas()
price = prices.iloc[0]['close']

if(position != 0):
    
    atr_file = open('ATR_When_Bought.txt','r')
    atr = atr_file.read()
    atr = float(atr)
    atr_file.close() 
    
    if((price - atr < 0) and (rsi >= 65)):
        signal = -1

    
class SellApp(EWrapper, EClient): #Declare class and override methods that we will need, such as the error and order
    def __init__(self):
        EClient.__init__(self, self)

        self.bitPrice = price
    def error(self, reqId, errorCode, errorString):
        print("Error: ", reqId, " ", errorCode, " ", errorString)
        
    def nextValidId(self, orderId: int):
        self.nextOrderId = orderId
        if(signal == -1):
            self.sellBit()
        else:
            print("No action needed")

    
    def orderStatus(self, orderId, status: str, filled: float, remaining: float, avgFillPrice: float, permId: int, parentId: int, lastFillPrice: float, clientId: int, whyHeld: str, mktCapPrice: float):
        return super().orderStatus(orderId, status, filled, remaining, avgFillPrice, permId, parentId, lastFillPrice, clientId, whyHeld, mktCapPrice)
    
    def openOrder(self, orderId, contract: Contract, order: Order, orderState):
        return super().openOrder(orderId, contract, order, orderState)
    
    def execDetails(self, reqId: int, contract: Contract, execution):
        return super().execDetails(reqId, contract, execution)
        
    def sellBit(self):
        contract = Contract() 
        contract.symbol = "BTC"
        contract.secType = "CRYPTO"
        contract.exchange = "PAXOS"
        contract.currency = "USD"
        contract.primaryExchange = "PAXOS"
        
        order1 = Order()    
        order1.action = "SELL"
        order1.orderType = "LMT" 
        order1.lmtPrice = SellApp().bitPrice - 5 # -5 from last price to give higher probability of trade execution
        order1.totalQuantity = position
        order1.tif = "Minutes"
        
        self.placeOrder(self.nextOrderId, contract, order1)
        
    def stop(self):
        self.done = True
        self.disconnect()


def BuySell():
    app = SellApp()
    app.nextOrderId = 0
    app.connect("127.0.0.1", 7496, 1)  # Should be a pause afterwards before invoking functions
    Timer(3, app.stop).start() #Sleep interval to allow time for connection to server
    
    runLoop(app)
    
BuySell()