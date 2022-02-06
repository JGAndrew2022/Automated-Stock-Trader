from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract

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

    return(currentPositions)

def sellStock():
    app = TestApp()
    app.connect("127.0.0.1", 7496, 1)  # Should be a pause afterwards before invoking functions
    time.sleep(1) #Sleep interval to allow time for connection to server

    contract = Contract() #Declare our contract
    contract.symbol = "AAPL"
    contract.secType = "STK"
    contract.exchange = "SMART"
    contract.currency = "USD"
    contract.primaryExchange = "NASDAQ"

    app.reqContractDetails(1, contract) #This will be replaced with the correct method to sell stock in the final stages of testing, for now this is a placeholder so that fees are not incurred upon every test
    print("Waiting for IB's API response for accounts positions requests...\n")
    time.sleep(3)
    runLoop(app)
    

def buyStock():
    buyApp = TestApp()
    buyApp.connect("127.0.0.1", 7496, 1)  # Should be a pause afterwards before invoking functions
    time.sleep(1) #Sleep interval to allow time for connection to server

    contract = Contract() #Declare our contract
    contract.symbol = "AAPL"
    contract.secType = "STK"
    contract.exchange = "SMART"
    contract.currency = "USD"
    contract.primaryExchange = "NASDAQ"

    buyApp.reqContractDetails(1, contract) #Place our order down here
    print("Waiting for IB's API response for accounts positions requests...\n")
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

if(MACDSignal == 1):
    buyStock()
elif(MACDSignal == -1 or RSISignal == -1):
    sellStock()
else:
    buyStock()