from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
from ibapi.order import Order

import time
from threading import Thread
import pandas as pd

#Three steps: definte the class, override EWrapper methods, connect to TWS
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
def newOrder(actionString, quant):
    #Fills out the order object 
    order1 = Order()    
    order1.action = actionString
    order1.orderType = "MKT"   
    order1.transmit = True
    order1.totalQuantity = quant 
    return order1

def newContract(symbl, primExch):
    #Declares a new contract
    contract = Contract() 
    contract.symbol = symbl
    contract.secType = "STK"
    contract.exchange = "SMART"
    contract.currency = "USD"
    contract.primaryExchange = primExch
    return contract

def buyStock():
    nextID = 11
    buyApp = TestApp()
    buyApp.connect("127.0.0.1", 7496, 2)  # Should be a pause afterwards before invoking functions
    time.sleep(1) #Sleep interval to allow time for connection to server

    contractObject = newContract("XLE", "ARCA")
    orderObject = newOrder("SELL", 5)
    buyApp.placeOrder(nextID, contractObject, orderObject)
    nextID += 1
    print("Waiting for IB's API response for order...\n")
    time.sleep(3)
    runLoop(buyApp)
    buyApp.disconnect()

buyStock()

