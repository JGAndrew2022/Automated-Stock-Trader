from twelvedata import TDClient  # I use Twelve Data to get realtime crypto data

td = TDClient(apikey='8600b4b5be4142e186c197b098338bbb')

# Construct the necessary time series
ts = td.time_series(
    symbol="BTC/USD",
    interval="1day",
    outputsize=1500,
    timezone="America/New_York",
)

# Make a pandas dataframe
indicators = ts.with_macd().with_rsi().as_pandas()
print(indicators)

length = len(indicators)
total = 0
buyPrice = 0
numTrades = 0
totalPercentGain = 0
i = length - 2
while (i > 0):
    if((indicators.iloc[i]['macd_hist'] > 0 and indicators.iloc[i+1]['macd_hist'] < 0) or (indicators.iloc[i]['rsi'] > 30 and indicators.iloc[i+1]['rsi'] < 30)):
        buyPrice = indicators.iloc[i]['open']
    elif((indicators.iloc[i]['macd_hist'] < 0 and indicators.iloc[i+1]['macd_hist'] > 0) or (indicators.iloc[i]['rsi'] < 70 and indicators.iloc[i+1]['rsi'] > 70)):
        gain = indicators.iloc[i]['open'] - buyPrice
        total += gain
        numTrades += 1
        percentGain = (gain/buyPrice)*100
        totalPercentGain += percentGain
    i -= 1
        
print(total)

averageGain = total/numTrades
print(averageGain)

avgPercGain = totalPercentGain/numTrades
print(avgPercGain)