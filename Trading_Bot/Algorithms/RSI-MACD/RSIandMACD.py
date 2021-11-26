from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
from ibapi.order import Order

import requests 
import substring
import json
import time
import pandas as pd

class TestApp(EWrapper, EClient): #Declare class and override methods that we will need, such as the error and order
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

def runLoop(sample):
    sample.run()
def getPosition():
    positionApp = TestApp()
    positionApp.connect("127.0.0.1", 7496, 0)  # Should be a pause afterwards before invoking functions
    time.sleep(1) #Sleep interval to allow time for connection to server

    positionApp.reqPositions() # associated callback: position
    print("Waiting for IB's API response for accounts positions requests...\n")
    time.sleep(3)
    runLoop(positionApp)
    currentPositions = positionApp.allPositions
    currentPositions.set_index('Account',inplace=True,drop=True) #set all_positions DataFrame index to "Account"
    if(currentPositions.empty):
        return 0
    else:
        return currentPositions.iat[0,1] #return the quantity of stock currently held in account

def newOrder(actionString, quant):
    #Fills out the order object 
    order1 = Order()    
    order1.action = actionString
    order1.orderType = "MKT"   
    order1.transmit = True
    order1.totalQuantity = quant 

def newContract(symbl, primExch):
    #Declares a new contract
    contract = Contract() 
    contract.symbol = symbl
    contract.secType = "STK"
    contract.exchange = "SMART"
    contract.currency = "USD"
    contract.primaryExchange = primExch

def sellStock(quantity):
    app = TestApp()
    app.connect("127.0.0.1", 7496, 1)  # Should be a pause afterwards before invoking functions
    time.sleep(1) #Sleep interval to allow time for connection to server

    contractObject = newContract("XLE", "ARCA")
    orderObject = newOrder("SELL", quantity)
    nextID = TestApp.nextValidOrderId
    app.placeOrder(nextID, contractObject, orderObject)
    nextID += 1
    print("Waiting for IB's API response for order...\n")
    time.sleep(3)
    runLoop(app)
    
def buyStock(quantity):
    buyApp = TestApp()
    buyApp.connect("127.0.0.1", 7496, 2)  # Should be a pause afterwards before invoking functions
    time.sleep(1) #Sleep interval to allow time for connection to server

    contractObject = newContract("XLE", "ARCA")
    orderObject = newOrder("BUY", quantity)
    nextID = TestApp.nextValidOrderId
    buyApp.placeOrder(nextID, contractObject, orderObject)
    nextID += 1
    print("Waiting for IB's API response for order...\n")
    time.sleep(3)
    runLoop(buyApp)

RSIUrl = 'https://api.twelvedata.com/rsi?symbol=AAPL&interval=1day&outputsize=30&apikey=8600b4b5be4142e186c197b098338bbb' 
MACDUrl = 'https://api.twelvedata.com/macd?symbol=AAPL&interval=1day&apikey=8600b4b5be4142e186c197b098338bbb'


rsi = requests.get(RSIUrl)  
rsiData = rsi.json()
rsiTxt = json.dumps(rsiData)
rsiList = rsiTxt.split("rsi")
del rsiList[0]
for i in range(0, len(rsiList)):
    newItem = rsiList[i]
    newItem = substring.substringByChar(newItem, startChar=":", endChar="}") 
    newItem = newItem.removeprefix(': "')
    newItem = newItem.removesuffix('"}')
    rsiList[i] = newItem

rsiList = [float(x) for x in rsiList] #we now have a list of RSI values

if(rsiList[0] < 70 and rsiList[1] > 70):
    RSISignal = -1
elif(rsiList[0] > 30 and rsiList[1] < 30):
    RSISignal = 1
else:
    RSISignal = 0

macd = requests.get(MACDUrl)
macdData = macd.json()
macdData = json.dumps(macdData)
macdList = macdData.split("macd_hist")
del macdList[0]
for j in range(0, len(macdList)-1):
    newMacdItem = macdList[j]
    newMacdItem = substring.substringByChar(newMacdItem, startChar=':', endChar='}') 
    newMacdItem = newMacdItem.removeprefix(': "')
    newMacdItem = newMacdItem.removesuffix('"}')
    macdList[j] = newMacdItem
del macdList[len(macdList) - 1]
macdList = [float(y) for y in macdList]

if(macdList[0] > 0 and macdList[1] < 0):
    MACDSignal = 1 #1 = buy
elif(macdList[0] < 0 and macdList[1] > 0):
    MACDSignal = -1 #-1 = sell
else:
    MACDSignal = 0 #0 = no action

if(MACDSignal == 1 or RSISignal == 1):
    if(getPosition() == 0):
        buyStock(15)
        print("buy stock")
elif(MACDSignal == -1 or RSISignal == -1):
    if(getPosition() != 0):
        sellStock(getPosition())
        print("sell stock")

else:
    print("no significant signal change")