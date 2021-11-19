from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
from ibapi.order import Order

import requests 
import substring
import json
import time
import pandas as pd

#This program has the same functionality as a point and figure chart

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
    def nextValidId(self, orderId: int):
        super().nextValidId(orderId)
        self.nextValidOrderId = orderId

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


#Algo part starts here
List = []
priceUrl = 'https://api.twelvedata.com/time_series?symbol=XLE&interval=30min&outputsize=3&apikey=8600b4b5be4142e186c197b098338bbb' #we will be using Twelve Data to receive price data from our stocks
atrUrl = 'https://api.twelvedata.com/atr?symbol=XLE&interval=1day&time_period=20&outputsize=24&apikey=8600b4b5be4142e186c197b098338bbb' 


atr = requests.get(atrUrl)  #this block collects the ATR data
atrData = atr.json()
atrTxt = json.dumps(atrData) #Use the json package to get information in string form
atrText = atrTxt.split("atr")
aTr = substring.substringByChar(atrText[1], startChar=":", endChar="}") #some string manipulation uisng the substring package
Atr = aTr.removeprefix(': "')
atR = Atr.removesuffix('"}') #this gives us a string that only contains float values, we can easily convert it to a float or int

price = requests.get(priceUrl) #same thing as ATR but this time we are getting the last close price
priceData = price.json()
priceToString = json.dumps(priceData)
text = priceToString.split('high":')
length = len(text)
for i in range(1, length-1):
    s = substring.substringByChar(text[i], startChar="c", endChar=",")
    x = substring.substringByChar(s, startChar=":", endChar=",")
    y = x.removeprefix(': "')
    f = y.removesuffix('",')
    List.append(f)
print(List[0]) #It may be useful to have multiple data points for price, rather than just one, which is we create a list of all data reported by alpha vantage

def calcReversal(): #this function with calculate a trend reversal on a point and figure chart
    reversal = 3*(float(atR)) #A reversal is 3 box sizes, which is the ATR in this case
    boxSize = float(atR)
    lastPrice = float(List[0])

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
        else:
            print("No significant price change.")
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
                sellStock(getPosition)
        else:
            print("No significant price change")
    if priceDif > 0 and direction == "True":
        if abs(priceDif) > boxSize:
            numBoxes = int(abs(priceDif)/boxSize)
            newBox = startBox+(numBoxes*boxSize)
            file2 = open("lastBox.txt", "w+")
            file2.write(str(newBox))
            file2.close()
            print("Option 3, Buy Signal, No change in position")
        else:
            print("No significant price change")
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
                buyStock(5)
        else:
            print("No significant price change")

calcReversal()