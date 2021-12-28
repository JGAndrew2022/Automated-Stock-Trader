from twelvedata import TDClient # I use Twelve Data to get realtime crypto data
import pandas as pd 

from sklearn.model_selection import train_test_split # Split data using scikit-learn package
from sklearn import linear_model # Machine learning linear model
from sklearn import preprocessing

# Initialize Twelve Data API client
td = TDClient(apikey='8600b4b5be4142e186c197b098338bbb')

# Construct the necessary time series, we use this to get out technical indicators
ts = td.time_series(
    symbol="BTC/USD",
    interval="1day",
    outputsize= 15,
    timezone="America/New_York",
)
pd.set_option('display.max_rows', None)
indicators = ts.with_macd().with_rsi(time_period = 15).with_ema(time_period = 15).as_pandas()
# Create a pandas dataframe with our 6 technical indicators that we will use
x_values = ['close', 'macd_hist', 'rsi'] # Our features are the technical indicators, our labels will
labels = []
indicator_data = []
sig_movement = float(indicators.iloc[0]['close'])/100 # We will consider a price movement to be significant if it is larger than 1% of the price of Bitcoin
cnt = len(indicators['rsi'])
j = cnt-2
while(j > 3): #since we do not have label data for the most recent week, we will exclude the 7 most recent datapoints
    RSI = indicators.iloc[j]['rsi']
    prev_RSI = indicators.iloc[j+1]['rsi']
    
    direc = RSI - prev_RSI # Is the RSI moving up or down? If so, by how much?
    
    if((prev_RSI >= 65 or prev_RSI <= 35) and (RSI <= 65 and RSI >= 35)):
        rsiChange = direc
    else:
        rsiChange = 0
        
        
    MACD = indicators.iloc[j]['macd_hist']
    prev_MACD = indicators.iloc[j+1]['macd_hist']
    
    if((prev_MACD > 0 and MACD < 0) or (prev_MACD < 0 and MACD > 0)):
        MACD_switch = MACD - prev_MACD
    else:
        MACD_switch = 0
    
    aroon_d = indicators.iloc[j]['aroon_down']
    aroon_u = indicators.iloc[j]['aroon_up']
    
    slow_k = indicators.iloc[j]['slow_k']
    slow_d = indicators.iloc[j]['slow_d']
    
    adx = indicators.iloc[j]['adx']
    
    
    initial_price = indicators.iloc[j]['close']
    final_price = indicators.iloc[j - 3]['close']
    dif = final_price - initial_price
    if(dif >= 0):
        label_data = 1
    elif(dif < 0):
        label_data = -1
    
    indicator_data.append([initial_price, final_price, label_data, RSI, rsiChange, MACD, MACD_switch, aroon_d, aroon_u, slow_k, slow_d, adx])
    
    j -= 1
    

features = pd.DataFrame(indicator_data, columns = ['initial','final','label_data', 'RSI', 'RSI Change', 'MACD', 'MACD Switch', 'Aroon Up', 'Aroon Down', 'Slow K', 'Slow D', 'ADX'])

print(features)

