# In order for our data to actually be useful for logisitcal regression, k-nearest-neighbor, or some other classifying model, the data needs to be processed in a way that the machine learning algorithms can 
# manipulate. We should process the data so that it can have a more or less constant relationship with the Bitcoin price. This way, our model can correctly predict negatively and positively correlated weights. 
from twelvedata import TDClient # I use Twelve Data to get realtime crypto data
import pandas as pd
import numpy as np

# Initialize Twelve Data API client
td = TDClient(apikey='8600b4b5be4142e186c197b098338bbb')

# Construct the necessary time series, we use this to get out technical indicators
ts = td.time_series(
    symbol="ETH/USD",
    interval="1day",
    outputsize= 1500,
    timezone="America/New_York",
)

indicators = ts.with_macd().with_rsi().as_pandas()
# Create a pandas dataframe with our 6 technical indicators that we will use
labels = []
indicator_data = []
cnt = len(indicators['close'])
print(indicators)
j = cnt-2

def isSupport(df,i):
    support = df['low'][i] < df['low'][i-1]  and df['low'][i] < df['low'][i+1] and df['low'][i+1] < df['low'][i+2] and df['low'][i-1] < df['low'][i-2]  
    return support
def isResistance(df,i):
    resistance = df['high'][i] > df['high'][i-1]  and df['high'][i] > df['high'][i+1] and df['high'][i+1] > df['high'][i+2] and df['high'][i-1] > df['high'][i-2]  
    return resistance
def upDownTrend(df,i,volatility):
    dif = np.absolute(df['close'][i] - df['close'][i+3])
    if(df['close'][i] > df['close'][i+3] and dif > volatility):
        return 1 # uptrend
    elif(df['close'][i] < df['close'][i+3] and dif > volatility):
        return -1 # downtrend
    else:
        return 0 # price is moving sideways


rangeList = []
for i in range(cnt):
    dayRange = np.absolute(indicators['open'] - indicators['close'])
    rangeList.append(dayRange)
volatility = np.mean(rangeList)

supp = 0
resist = 0
while(j > 3): #since we do not have label data for the most recent 4 days, we will exclude the 4 most recent datapoints
    if isSupport(indicators,i):
        supp = indicators['low'][i]
    elif isResistance(indicators,i):
        resist = indicators['high'][i]
    
    trend = upDownTrend(indicators, i, volatility)
    if(trend == 1):
        if(resist - indicators['close'][i] > 0):
            dist = resist - indicators['close'][i]
            brokeThru = None
        else:
            dist = None
            brokeThru = resist - indicators['close'][i]
    elif(trend == -1):
        if(supp - indicators['close'][i] < 0):
            dist = supp - indicators['close'][i]
            brokeThru = None
        else:
            dist = None
            brokeThru = supp - indicators['close'][i]
    else:
        dist = None
        brokeThru = None
    
    indicator_data.append([trend, dist, brokeThru])
    
    initial_price = indicators.iloc[j]['close']
    final_price = indicators.iloc[j - 4]['close']
    dif = initial_price - final_price
    if(dif >= 0):
        labels.append(-1)
    elif(dif < 0):
        labels.append(1)
        
    j -= 1
features = pd.DataFrame(indicator_data, columns = ['Trend', 'Distance From S or R', 'Broken Thru S or R'])


