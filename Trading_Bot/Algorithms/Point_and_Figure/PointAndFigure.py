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
    positionApp = GetPositionApp() #defined later
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
position = getPosition()

# Algo part starts here
td = TDClient(apikey='8600b4b5be4142e186c197b098338bbb')

# Construct the necessary time series
ts = td.time_series(
    symbol="BTC/USD",
    interval="30min",
    outputsize=3,
    timezone="America/New_York",
)

# Make a pandas dataframe
df = ts.as_pandas()


indicators = ts.with_atr().as_pandas()

atr = indicators.iloc[0]['atr']
price = indicators.iloc[0]['close']

reversal = 3*(float(atr)) #A reversal is 3 box sizes, which is the ATR in this case
boxSize = float(atr)
lastPrice = float(price)
    
file1 = open("direction.txt","r") #for this project, I am using text files to store the value of desired variables outside the program
direction = file1.read() #get the direction of the last movement
if direction != "True" and direction != "False":
    print("Error! File direction.txt contains an invalid string.")
file1.close()

file = open("lastBox.txt","r")
startBox = file.read() #get the last box price
file.close()
startBox = float(startBox)

priceDif = lastPrice - startBox 

print(direction)
if priceDif < 0 and direction == "False":
    if abs(priceDif) > boxSize:
        numBoxes = int(abs(priceDif)/boxSize)
        newBox = startBox-(numBoxes*boxSize)
        file2 = open("lastBox.txt", "w+")
        file2.write(str(newBox))
        file2.close()
        print("Option 1, Sell Signal, No change in position") #During testing, print statements make it easy to see if the algorithm is working correctly or not
        signal = 0
    else:
        print("No significant price change.")
        signal = 0
if priceDif < 0 and direction == "True":
    if abs(priceDif) > reversal:
        numBoxes = int(abs(priceDif)/boxSize)
        newBox = startBox-(numBoxes*boxSize)
        newDirec = "False"
        file2 = open("lastBox.txt", "w+")
        file2.write(str(newBox))
        file2.close()
        file3 = open("direction.txt", "w+")
        file3.write(str(newDirec))
        file3.close()
        print("Option 2, Sell Signall, stocks held in current position should be sold")
        if(getPosition() != 0):
             signal = -1
    else:
        print("No significant price change")
        signal = 0
if priceDif > 0 and direction == "True":
    if abs(priceDif) > boxSize:
        numBoxes = int(abs(priceDif)/boxSize)
        newBox = startBox+(numBoxes*boxSize)
        file2 = open("lastBox.txt", "w+")
        file2.write(str(newBox))
        file2.close()
        print("Option 3, Buy Signal, No change in position")
        signal = 0
    else:
        print("No significant price change")
        signal = 0
if priceDif > 0 and direction == "False":
    if abs(priceDif) > reversal:
        numBoxes = int(abs(priceDif)/boxSize)
        newBox = startBox+(numBoxes*boxSize)
        newDirec = "True"
        file2 = open("lastBox.txt", "w+")
        file2.write(str(newBox))
        file2.close()
        file3 = open("direction.txt", "w+")
        file3.write(str(newDirec))
        file3.close()
        print("Option 4, Buy Signal, Stock should be added to position")
    if(getPosition() == 0):
        signal = 1
    else:
        print("No significant price change")
        signal = 0
            
class BuySellApp(EWrapper, EClient): #Declare class and override methods that we will need, such as the error and order
    def __init__(self):
        EClient.__init__(self, self)

        self.price = int(indicators.iloc[0]['close']) 
        
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
        order1.lmtPrice = BuySellApp().price + 1 
        order1.totalQuantity = 0.5
        order1.tif = "Minutes"
        
        self.placeOrder(self.nextOrderId, contract, order1)
        
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
        order1.lmtPrice = BuySellApp().price-1
        order1.totalQuantity = position
        order1.tif = "Minutes"
        
        self.placeOrder(self.nextOrderId, contract, order1)
        
    def stop(self):
        self.done = True
        self.disconnect()


def BuySell():
    app = BuySellApp()
    app.nextOrderId = 0
    app.connect("127.0.0.1", 7496, 1)  # Should be a pause afterwards before invoking functions
    Timer(3, app.stop).start() #Sleep interval to allow time for connection to server
    
    runLoop(app)
    
BuySell()

