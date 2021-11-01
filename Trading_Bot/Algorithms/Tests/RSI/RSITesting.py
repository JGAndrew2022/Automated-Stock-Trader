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
LongtermRSIURL = 'https://api.twelvedata.com/rsi?symbol=AAPL&interval=1month&outputsize=30&apikey=8600b4b5be4142e186c197b098338bbb' #We compare RSI to long-term RSI to try to minimize false negatives or positives

def buySignal(tf):
    file1 = open("RSI-signal.txt", "w+")
    file1.write(str(tf))
    file1.close()

def sellSignal(tf):
    file1 = open("RSI-sell-signal.txt", "w+")
    file1.write(str(tf))
    file1.close()

def increaseFrequency(tf):
    file2 = open("frequency.txt", "w+")
    file2.write(str(tf))
    file2.close()

LTRsi = requests.get(LongtermRSIURL)  #Lines 9-31 get the raw JSON data into an organized list that we can easily manipulate
LTRsiData = LTRsi.json()
LTRsiTxt = json.dumps(LTRsiData)
LTRsiList = LTRsiTxt.split("rsi")
newLTList = []
i = 0
for i in range(1, len(LTRsiList)):
    newItem = substring.substringByChar(LTRsiList[i], startChar=":", endChar="}") #Some string manipulation uisng the substring package
    newItem = newItem.removeprefix(': "')
    newItem = newItem.removesuffix('"}')
    newLTList.append(newItem)
newLTList = [float(x) for x in newLTList]

rsi = requests.get(RSIUrl)  
rsiData = rsi.json()
rsiTxt = json.dumps(rsiData)
rsiList = rsiTxt.split("rsi")
newList = []
i = 0
for i in range(1, len(rsiList)):
    newItem = substring.substringByChar(rsiList[i], startChar=":", endChar="}") 
    newItem = newItem.removeprefix(': "')
    newItem = newItem.removesuffix('"}')
    newList.append(newItem)
    newList = [float(x) for x in newList]

xValueList = []
for i in range(-30, 0):
    xValueList.append(i) #create x values from 1-30 to plot

LTdiff = newLTList[0] - newLTList[1]
diff = newList[0] - newList[1]

if(newList[0] <= 30 or newList[1] <= 30): #if short-term and long-term both show reasonable buy or sell signals, we can place a buy or sell before the point and figure chart indicates to do so
    if((newList[0] >= 30 and newList[0] <= 35) and (newLTList[0] <= 35 and LTdiff > 0)):
        buyStock()
else:
    buySignal(False)
if(newList[0] >= 70 or newList[1] >= 70):
    if((newList[0] <= 70 and newList[0] >= 65) and (newLTList[0] >= 65 and LTdiff < 0)):
        sellStock()
else:
    sellSignal(False)



