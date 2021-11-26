import pandas as pd
import requests 
import json

RSIUrl = 'https://api.twelvedata.com/rsi?symbol=AAPL&interval=1day&outputsize=30&format=json&apikey=8600b4b5be4142e186c197b098338bbb' 
LongtermRSIURL = 'https://api.twelvedata.com/rsi?symbol=AAPL&interval=1month&outputsize=15&apikey=8600b4b5be4142e186c197b098338bbb' #We compare RSI to long-term RSI to try to minimize false negatives or positives

rsi = requests.get(RSIUrl)
rsiJson = rsi.json()
dataframe = pd.read_json(rsiJson)

print(dataframe)



