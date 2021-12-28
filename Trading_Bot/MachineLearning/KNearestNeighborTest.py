from twelvedata import TDClient # I use Twelve Data to get realtime crypto data
import pandas as pd # Linear algebra, not used yet
import numpy as np

from sklearn.model_selection import train_test_split # Split data using scikit-learn package
from sklearn import neighbors # Machine learning linear model
from sklearn import preprocessing

# Initialize client
td = TDClient(apikey='8600b4b5be4142e186c197b098338bbb')

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
for j in range(cnt):
    dayRange = np.absolute(indicators['open'][j] - indicators['close'][j])
    rangeList.append(dayRange)
volatility = np.mean(rangeList)

supp = 0
resist = 0
i = cnt-4
while(i > 3): #since we do not have label data for the most recent 4 days, we will exclude the 4 most recent datapoints
    if isSupport(indicators,i):
        supp = indicators['low'][i]
    elif isResistance(indicators,i):
        resist = indicators['high'][i]
    
    trend = upDownTrend(indicators, i, volatility)
    if(trend == 1):
        if(resist - indicators['close'][i] > 0):
            dist = resist - indicators['close'][i]
            brokeThru = 0
        else:
            dist = 0
            brokeThru = resist - indicators['close'][i]
    elif(trend == -1):
        if(supp - indicators['close'][i] < 0):
            dist = supp - indicators['close'][i]
            brokeThru = 0
        else:
            dist = 0
            brokeThru = supp - indicators['close'][i]
    else:
        dist = 0
        brokeThru = 0
    
    indicator_data.append([trend, dist, brokeThru])
    
    initial_price = indicators.iloc[i]['close']
    final_price = indicators.iloc[i - 4]['close']
    dif = initial_price - final_price
    if(dif >= 0):
        labels.append(-1)
    elif(dif < 0):
        labels.append(1)
        
    i -= 1
features = pd.DataFrame(indicator_data, columns = ['Trend', 'Distance From S or R', 'Broken Thru S or R'])


scaler = preprocessing.StandardScaler().fit(features)
new_features = scaler.transform(features)


x_train, x_test, y_train, y_test = train_test_split(new_features, labels, test_size=0.3, random_state=1)


model = neighbors.KNeighborsClassifier(n_neighbors=3)
model.fit(x_train, y_train)

model.predict(x_test)

print(model.score(x_test, y_test))