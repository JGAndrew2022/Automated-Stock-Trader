from threading import Timer
import time

import pandas as pd
from ibapi.client import EClient
from ibapi.contract import Contract
from ibapi.order import *
from ibapi.wrapper import EWrapper
from twelvedata import TDClient  # I use Twelve Data to get realtime crypto data

class GetPositionApp(EWrapper, EClient): #Declare class and override methods that we will need, such as the error and order
    def __init__(self):
        EClient.__init__(self, self)

        self.allPositions = pd.DataFrame([], columns = ['Account','Symbol', 'Quantity', 'Average Cost', 'Sec Type'])
        self.cashBal = 0
    def error(self, reqId, errorCode, errorString):
        print("Error: ", reqId, " ", errorCode, " ", errorString)
    
    def position(self, account: str, contract: Contract, position: float, avgCost: float):
        super().position(account, contract, position, avgCost)
        index = str(account)+str(contract.symbol)
        self.allPositions.loc[index]= account, contract.symbol, position, avgCost, contract.secType
    
    def positionEnd(self):
        super().positionEnd()
        self.disconnect()
    
    def accountSummary(self, reqId: int, account: str, tag: str, value: str, currency: str):
        super().accountSummary(reqId, account, tag, value, currency)
        if (tag == "CashBalance"):
            self.cashBal = value
        
    def accountSummaryEnd(self, reqId: int):
        super().accountSummaryEnd(reqId)
        self.disconnect()

def runLoop(sample):
    sample.run()

def getAccountValue():
    accountApp = GetPositionApp()
    accountApp.connect("127.0.0.1", 7496, 9)
    time.sleep(1)
    
    accountApp.reqAccountSummary(9001, "All", "$LEDGER:ALL") # associated callback: accountSummary()
    print("Waiting for IB's API response for accounts requests...\n")
    time.sleep(1)
    accountApp.cancelAccountSummary(9001)
    runLoop(accountApp)
    cashBalance = accountApp.cashBal
    return cashBalance
    
def getPosition():
    positionApp = GetPositionApp() #defined later
    positionApp.connect("127.0.0.1", 7496, 6)  # Should be a pause afterwards before invoking functions
    time.sleep(1) #Sleep interval to allow time for connection to server

    positionApp.reqPositions() # associated callback: position
    print("Waiting for IB's API response for accounts positions requests...\n")
    time.sleep(1)
    runLoop(positionApp)
    currentPositions = positionApp.allPositions
    currentPositions.set_index('Account',inplace=True,drop=True) #set all_positions DataFrame index to "Account"
    if(currentPositions.empty):
        return 0
    else:
        return currentPositions.iat[0,1] #return the quantity of stock currently held in account
cash = float(getAccountValue()) - 10
position = getPosition()

td = TDClient(apikey='8600b4b5be4142e186c197b098338bbb')

# Construct the necessary time series
ts = td.time_series(
    symbol="BTC/USD",
    interval="30min",
    outputsize=3,
    timezone="America/New_York",
)

# Make a pandas dataframe
indicators = ts.with_macd().with_rsi().with_atr().as_pandas()
atr_val = indicators.iloc[0]['atr']
if(indicators.iloc[0]['rsi'] < 70 and indicators.iloc[1]['rsi'] > 70):
    RSISignal = -1
elif(indicators.iloc[0]['rsi'] > 30 and indicators.iloc[1]['rsi'] < 30):
    RSISignal = 1
else:
    RSISignal = 0

if(indicators.iloc[0]['macd_hist'] > 0 and indicators.iloc[1]['macd_hist'] < 0):
    MACDSignal = 1 #1 = buy
elif(indicators.iloc[0]['macd_hist'] < 0 and indicators.iloc[1]['macd_hist'] > 0):
    MACDSignal = -1 #-1 = sell
else:
    MACDSignal = 0 #0 = no action

if(RSISignal == 1 or MACDSignal == 1):
    signal = 1
    print('Buy')
elif(RSISignal == -1 or MACDSignal == -1):
    signal = -1
    print('Sell')
else:
    signal = 0
    print('No Change')

td2 = TDClient(apikey='8600b4b5be4142e186c197b098338bbb')


ts2 = td2.time_series( # We create a second time series using the Twelve Data API so that we can ensure our buy/sell methods get the proper price value
    symbol="BTC/USD",
    interval="1min",
    outputsize=2,
    timezone="America/New_York",)

ts2_pd = ts2.as_pandas()

class BuySellApp(EWrapper, EClient): #Declare class and override methods that we will need, such as the error and order
    def __init__(self):
        EClient.__init__(self, self)

        self.price = int(ts2_pd.iloc[0]['close'])
        
    def error(self, reqId, errorCode, errorString):
        print("Error: ", reqId, " ", errorCode, " ", errorString)
        
    def nextValidId(self, orderId: int):
        self.nextOrderId = orderId
        if(signal == 1):
            self.buyBit()
        elif(signal == -1):
            self.sellBit()

    
    def orderStatus(self, orderId, status: str, filled: float, remaining: float, avgFillPrice: float, permId: int, parentId: int, lastFillPrice: float, clientId: int, whyHeld: str, mktCapPrice: float):
        return super().orderStatus(orderId, status, filled, remaining, avgFillPrice, permId, parentId, lastFillPrice, clientId, whyHeld, mktCapPrice)
    
    def openOrder(self, orderId, contract: Contract, order: Order, orderState):
        return super().openOrder(orderId, contract, order, orderState)
    
    def execDetails(self, reqId: int, contract: Contract, execution):
        return super().execDetails(reqId, contract, execution)
    
    def buyBit(self):
        contract = Contract() 
        contract.symbol = "BTC"
        contract.secType = "CRYPTO"
        contract.exchange = "PAXOS"
        contract.currency = "USD"
        contract.primaryExchange = "PAXOS"
        
        order1 = Order()    
        order1.action = "BUY"
        order1.orderType = "LMT" 
        order1.lmtPrice = BuySellApp().price + 5
        order1.totalQuantity = 0.5
        order1.tif = "Minutes"
        
        self.placeOrder(self.nextOrderId, contract, order1)
        
        atr_file = open('../Profit_Taking/ATR_When_Bought.txt','w')
        atr_file.write(atr_val)
        atr_file.close() 
        
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
        order1.lmtPrice = BuySellApp().price - 5
        order1.totalQuantity = position
        order1.tif = "Minutes"
        print("selling")
        
        self.placeOrder(self.nextOrderId, contract, order1)
        
    def stop(self):
        self.done = True
        self.disconnect()


def BuySell():
    app = BuySellApp()
    app.nextOrderId = 0
    app.connect("127.0.0.1", 7496, 7)  # Should be a pause afterwards before invoking functions
    Timer(3, app.stop).start() #Sleep interval to allow time for connection to server
    
    runLoop(app)
    
BuySell()


