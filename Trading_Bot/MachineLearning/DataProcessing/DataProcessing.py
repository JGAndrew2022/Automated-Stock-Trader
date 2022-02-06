# In order for our data to actually be useful for logisitcal regression, k-nearest-neighbor, or some other classifying model, the data needs to be processed in a way that the machine learning algorithms can 
# manipulate. We should process the data so that it can display a relationship with the Bitcoin price. This way, our model can correctly predict negatively and positively correlated weights. 
import pandas as pd
import numpy as np
from TechnicalIndicatorsClass import TechnicalIndicators as tech

dominanceDF = pd.read_csv('btc_dominance.csv')
historicalDataDF = pd.read_csv('coin_Bitcoin.csv')
cnt = len(dominanceDF)

def isSupport(df,i):
    support = df['low'][i] < df['low'][i-1]  and df['low'][i] < df['low'][i+1] and df['low'][i+1] < df['low'][i+2] and df['low'][i-1] < df['low'][i-2]  
    return support
def isResistance(df,i):
    resistance = df['high'][i] > df['high'][i-1]  and df['high'][i] > df['high'][i+1] and df['high'][i+1] > df['high'][i+2] and df['high'][i-1] > df['high'][i-2]  
    return resistance
def upDownTrendShort(df,i,volatility):
    dif = np.absolute(df['close'][i] - df['close'][i-3])
    dif /= df['open'][i]
    if(df['close'][i] > df['close'][i-3] and dif > volatility):
        return 1 # uptrend
    elif(df['close'][i] < df['close'][i-3] and dif > volatility):
        return -1 # downtrend
    else:
        return 0 # price is moving sideways

rangeList = []
for j in range(cnt):
    dayRange = np.absolute(historicalDataDF['open'][j] - historicalDataDF['close'][j])
    dayRange /= historicalDataDF['open'][j] # Make the range a percentage
    rangeList.append(dayRange)
volatility = np.mean(rangeList) #average volatility

supp = 0
resist = 0
k = 4
indicator_data = []
labels_list = []

techInd = tech(historicalDataDF)
ema = techInd.EMA(14)
atr = techInd.ATR(14)
macd, signal, hist = techInd.MACD(12, 26)
rsi, avgG, avgL = techInd.RSI(14)

while(k < cnt-2): #since we do not have label data for the most recent 4 days, we will exclude the 4 most recent datapoints
    if isSupport(historicalDataDF,k):
        supp = historicalDataDF['low'][k]
    elif isResistance(historicalDataDF,k):
        resist = historicalDataDF['high'][k]
    
    shortTrend = upDownTrendShort(historicalDataDF, k, volatility) # Is the current trend up or down?
    if(shortTrend == 1):
        if(resist - historicalDataDF['close'][k] > 0):
            dist = resist - historicalDataDF['close'][k] # Distance from resistance level
            brokeThru = 0 # In this case, the price has not broken through resistance
        else:
            dist = 0 # Distance below resistance is 0 since the price has broken through
            brokeThru = resist - historicalDataDF['close'][k] # Distance above resistance level, setting up the parameters in this way yields greater accurancy than a single paremeter
    elif(shortTrend == -1):
        if(supp - historicalDataDF['close'][k] < 0):
            dist = supp - historicalDataDF['close'][k]
            brokeThru = 0
        else:
            dist = 0
            brokeThru = supp - historicalDataDF['close'][k]
    else:
        dist = 0
        brokeThru = 0
    
    dominance = dominanceDF['Date'][k] - dominanceDF['Date'][k-7] # How has the market dominance of bitcoin changed over the past week?
    
    initial_price = historicalDataDF.iloc[k]['close']
    final_price = historicalDataDF.iloc[k + 4]['close']
    dif = initial_price - final_price
    if(dif >= 0 and np.absolute(dif) >= volatility):
        label = -1 # Sell
    elif(dif < 0 and np.absolute(dif) >= volatility):
        label = 1 # Buy
    else:
        label = 0 # Hold
    
    close = historicalDataDF['close'][k]
    
    indicator_data.append([close, shortTrend, dist, brokeThru, dominance, ema[k]/close, atr[k]/close, macd[k]/close, signal[k]/close, hist[k]/close, rsi[k], avgG[k], avgL[k]])
    labels_list.append([label])
        
    k += 1
features = pd.DataFrame(indicator_data, columns = [' close', 'Short-Term Trend', 'Distance From S or R', 'Broken Thru S or R', 'Change In BTC Dominance', 'EMA', 'ATR', 'MACD', 'MACD Signal', 'MACD Histogram', 'RSI', 'Average Gain', 'Average Loss'])
label_df = pd.DataFrame(labels_list, columns=['label'])

features.to_csv('..\dfeatures.csv',index=False)
label_df.to_csv('..\labels.csv',index=False)

print(features)