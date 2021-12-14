# In order for our data to actually be useful for logisitcal regression, k-nearest-neighbor, or some other classifying model, the data needs to be actually useful. We should process the data so that
# it can have a more or less constant relationship with the Bitcoin price. This way, our model can correctly predict negatively and positively correlated weights. 
from twelvedata import TDClient # I use Twelve Data to get realtime crypto data
import pandas as pd

# Initialize Twelve Data API client
td = TDClient(apikey='8600b4b5be4142e186c197b098338bbb')

# Construct the necessary time series, we use this to get out technical indicators
ts = td.time_series(
    symbol="BTC/USD",
    interval="4h",
    outputsize=4000,
    timezone="America/New_York",
)

indicators = ts.with_macd().with_obv().with_adx().with_aroon().with_rsi().with_stoch().as_pandas()
# Create a pandas dataframe with our 6 technical indicators that we will use
x_values = ['obv', 'macd_hist', 'adx', 'aroon_down', 'aroon_up', 'rsi', 'slow_k', 'slow_d'] # Our features are the technical indicators, our labels will
labels = []
std_dev = 295 # This is roughly equal to Bitcoin's current daily volatility, but we can request this figure after basic testing.
rsi_data = []
cnt = len(indicators['obv'])
j = 1
while(j < (cnt - 42)):
    RSI = indicators.iloc[j]['rsi']
    prev_RSI = indicators.iloc[j-1]['rsi']
    
    direc = RSI - prev_RSI # Is the RSI moving up or down? If so, by how much?
    
    if(RSI >= 65):
        is_sig_rsi = RSI - 65 # Is the RSI above 65? If so, by how much?
        was_sig_rsi = 0
    elif(RSI <= 35):
        is_sig_rsi = RSI - 35 # Is the RSI below 35? If so, by how much?
        was_sig_rsi = 0
    elif(prev_RSI >= 65 or prev_RSI <= 35):
        is_sig_rsi = 0
        was_sig_rsi = direc
    else:
        is_sig_rsi = 0
        was_sig_rsi = 0
        
        
    MACD = indicators.iloc[j]['macd_hist']
    prev_MACD = indicators.iloc[j-1]['macd_hist']
    
    if((prev_MACD > 0 and MACD < 0) or (prev_MACD < 0 and MACD > 0)):
        MACD_switch = MACD - prev_MACD
    else:
        MACD_switch = 0
        
    obv = indicators.iloc[j]['obv']
    
    aroon_d = indicators.iloc[j]['aroon_down']
    aroon_u = indicators.iloc[j]['aroon_up']
    
    rsi_data.append([direc, is_sig_rsi, was_sig_rsi, MACD, MACD_switch, obv, aroon_d, aroon_u])
    j += 1
features = pd.DataFrame(rsi_data, columns = ['RSI_Direc', 'Is_RSI_Sig', 'Was_RSI_Sig', 'MACD', 'MACD_Switch', 'OBV', 'Aroon_Up', 'Aroon_Down'])
    
for i in range(cnt - 42):
    initial_price = indicators.iloc[i]['close']
    final_price = indicators.iloc[i+42]['close']
    dif = initial_price - final_price
    if(dif > 0):
        labels.append(0)
    elif(dif < 0):
        labels.append(1)