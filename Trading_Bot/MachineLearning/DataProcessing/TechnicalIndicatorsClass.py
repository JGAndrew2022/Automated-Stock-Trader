import pandas as panda
import numpy as np

class TechnicalIndicators:
    
    # Price data should be in the form of a pandas dataframe
    def __init__(self, pd: panda.DataFrame):
        self.priceData = pd
        self.cnt = len(self.priceData) 
    
    # Returns a list of rsi values for a set of price data
    def RSI(self, period: int):
        self.rsiList = []
        self.avgGainList = []
        self.avgLossList = []
        for self.i in range(period, self.cnt):
            self.rsiVal = 100 - (100/(1 + ((self.AverageGain(self.i, period)/period)/(self.AverageLoss(self.i, period)/period))))
            self.avgGainList.append(self.AverageGain(self.i, period))
            self.avgLossList.append(self.AverageLoss(self.i, period))
            self.rsiList.append(self.rsiVal)
        return self.rsiList, self.avgGainList, self.avgLossList
    
    # Returns the average gain for all days that price rose within a given period
    def AverageGain(self, startPoint: int, period: int):
        self.gain = []
        for self.j in range(startPoint - period, startPoint):
            if(self.priceData['close'][self.j] > self.priceData['open'][self.j]):
                self.gain.append((self.priceData['close'][self.j] - self.priceData['open'][self.j])/self.priceData['open'][self.j])     
        return np.average(self.gain)*100
    
    # Returns the average gain for all days that price rose within a given period
    def AverageLoss(self, startPoint: int, period: int):
        self.loss = []
        for self.k in range(startPoint - period, startPoint):
            if(self.priceData['close'][self.k] <= self.priceData['open'][self.k]):
                self.loss.append((self.priceData['open'][self.k] - self.priceData['close'][self.k])/self.priceData['open'][self.k])
        return np.average(self.loss)*100
    
    # Returns the EMA for a long period, such as 26 days, subtracted from the EMA of a short period, such as 12 days
    def MACD(self, shortPeriod: int, longPeriod: int):
        self.macdList = []
        self.signalList = []
        self.macdHistList = []
        self.emaShort = self.EMA(shortPeriod)
        self.emaLong = self.EMA(longPeriod)
        
        for self.l in range(longPeriod, self.cnt):
            self.macdList.append(self.emaShort[self.l] - self.emaLong[self.l])
        
        self.signal = self.macdEMA(9)
        for self.p in range(len(self.macdList)):
            self.signalList.append(self.signal[self.p])
        
        for self.r in range(len(self.macdList)):
            self.macdHistList.append(self.macdList[self.r] - self.signalList[self.r])
        
        return self.macdList, self.signalList, self.macdHistList
    
    # Returns a list of exponential moving averages (EMA) for a period, which is a type of moving average (MA) that places a greater weight and significance on the most recent data points.
    def EMA(self, period: int):
        self.priceValues = []
        self.emaList = []
        for self.m in range(0, period):
            self.priceValues.append(self.priceData['close'][self.m])
            self.prevEMA = np.average(self.priceValues)
            self.emaList.append(self.prevEMA)
            
        for self.n in range(period, self.cnt):
            self.newEMA = self.priceData['close'][self.n]*(2/(period+1))
            self.newEMA += self.prevEMA*(1-(2/(period+1)))
            self.prevEMA = self.newEMA
            self.emaList.append(self.newEMA)
        return self.emaList
    
    # Returns a list of exponential moving averages for the MACD, which is used to create the MACD Signal Line
    def macdEMA(self, period: int):
        self.macdValues = []
        self.macdEmaList = []
        for self.o in range(0, period):
            self.macdValues.append(self.macdList[self.o])
            self.prevVal = np.average(self.macdValues)
            self.macdEmaList.append(self.prevVal)
            
        for self.q in range(period, len(self.macdList)):
            self.newMEMA = self.macdList[self.q]*(2/(period+1))
            self.newMEMA += self.prevVal*(1-(2/(period+1)))
            self.prevVal = self.newMEMA
            self.macdEmaList.append(self.newMEMA)
        return self.macdEmaList

    def ATR(self, period: int):
        self.atrList = []
        self.trueRangeList = []
        
        for self.s in range(1, self.cnt):
            if((self.priceData['high'][self.s] - self.priceData['low'][self.s] >= np.absolute(self.priceData['high'][self.s] - self.priceData['close'][self.s-1])) and (self.priceData['high'][self.s] - self.priceData['low'][self.s] >= np.absolute(self.priceData['low'][self.s] - self.priceData['close'][self.s-1]))):
                self.trueRangeList.append(self.priceData['high'][self.s] - self.priceData['low'][self.s])
            elif((np.absolute(self.priceData['high'][self.s] - self.priceData['close'][self.s-1]) >= self.priceData['high'][self.s] - self.priceData['low'][self.s]) and (np.absolute(self.priceData['high'][self.s] - self.priceData['close'][self.s-1]) >= np.absolute(self.priceData['low'][self.s] - self.priceData['close'][self.s-1]))):
                self.trueRangeList.append(np.absolute(self.priceData['high'][self.s] - self.priceData['close'][self.s-1]))
            else:
                self.trueRangeList.append(np.absolute(self.priceData['low'][self.s] - self.priceData['close'][self.s-1]))
        for self.t in range(period, self.cnt):
            self.atrList.append(np.average(self.trueRangeList[self.t-period:self.t]))  
        return self.atrList