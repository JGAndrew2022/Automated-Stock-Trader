from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract

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
def main():
    positionApp = TestApp()
    positionApp.connect("127.0.0.1", 7496, 0)  # Should be a pause afterwards before invoking functions
    #Start the socket in a thread
    time.sleep(1) #Sleep interval to allow time for connection to server

    positionApp.reqPositions() # associated callback: position
    print("Waiting for IB's API response for accounts positions requests...\n")
    time.sleep(3)
    api_thread = Thread(target=runLoop(positionApp), daemon=True)
    api_thread.start()
    currentPositions = positionApp.allPositions
    currentPositions.set_index('Account',inplace=True,drop=True) #set all_positions DataFrame index to "Account"

    print(currentPositions)


if __name__ == "__main__":
    main()