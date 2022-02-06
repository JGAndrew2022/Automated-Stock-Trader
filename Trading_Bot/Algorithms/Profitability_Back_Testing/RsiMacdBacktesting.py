from twelvedata import TDClient  # I use Twelve Data to get realtime crypto and stock market data

td = TDClient(apikey='8600b4b5be4142e186c197b098338bbb')

# Construct the necessary time series
ts = td.time_series(
    symbol="VOO", # Popular S&P 500 index fund
    interval="1day",
    outputsize=5000,
    timezone="America/New_York",
)

# Make a pandas dataframe
indicators = ts.with_macd().with_rsi().with_atr().as_pandas()

length = len(indicators)
total = 0
buyPrice = 0
numTrades = 0
totalPercentGain = 0
atr = 0
rangePrice = 0
activeTrade = False
i = length - 3
while (i > 0):
    if((indicators.iloc[i]['macd_hist'] > 0 and indicators.iloc[i + 1]['macd_hist'] < 0) or (indicators.iloc[i]['rsi'] > 30 and indicators.iloc[i+1]['rsi'] < 30)): #RSI and MACD buy algos
        buyPrice = indicators.iloc[i]['close']
        activeTrade = True
        atr = indicators.iloc[i]['atr']
        rangePrice = buyPrice + atr
    elif((activeTrade == True) and (indicators.iloc[i+1]['open'] < rangePrice) and (indicators.iloc[i+1]['rsi'] > 65)): # Profit-taking sell algo
        gain = indicators.iloc[i]['close'] - buyPrice
        if(gain <= 0):
            activeTrade = True
        else:
            total += gain
            numTrades += 1
            percentGain = (gain/buyPrice)*100
            totalPercentGain += percentGain
            activeTrade = False
    elif((activeTrade == True) and ((indicators.iloc[i]['macd_hist'] < 0 and indicators.iloc[i + 1]['macd_hist'] > 0) or (indicators.iloc[i]['rsi'] < 70 and indicators.iloc[i+1]['rsi'] > 70))): #RSI and MACD sell algos
        gain = indicators.iloc[i]['close'] - buyPrice
        if(gain <= 0):
            activeTrade = True
        else:
            total += gain
            numTrades += 1
            percentGain = (gain/buyPrice)*100
            totalPercentGain += percentGain
            activeTrade = False
    i -= 1
        
print(total)

averageGain = total/numTrades
print('Average gain per trade: ', averageGain)

avgPercGain = totalPercentGain/numTrades
print('Average percent gain per trade: ', avgPercGain)

trdsPrYr = numTrades/(5000/365)
print('Trades per year: ', trdsPrYr)

GainPrYr = 1000*(1+(avgPercGain/100))**(trdsPrYr) - 1000
print('Gain after one year year from an initial investment of $1,000: ', GainPrYr)

ttlPercGnPrYr = GainPrYr/10
print('Total percent gain per year: ', ttlPercGnPrYr)