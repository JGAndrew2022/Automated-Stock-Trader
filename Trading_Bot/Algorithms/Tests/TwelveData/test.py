import requests 
import substring
import json

atrUrl = 'https://api.twelvedata.com/atr?symbol=AAPL&interval=1day&time_period=20&outputsize=24&apikey=8600b4b5be4142e186c197b098338bbb'

atr = requests.get(atrUrl)  #this block collects the ATR data
atrData = atr.json()
atrTxt = json.dumps(atrData) #Alpha Vantage gives a dict() with only two mappings, so we have to split each individual ATR for each day from the second mapping
atrText = atrTxt.split("atr")
aTr = substring.substringByChar(atrText[1], startChar=":", endChar="}") #some string manipulation uisng the substring package
Atr = aTr.removeprefix(': "')
atR = Atr.removesuffix('"}') #this gives us a string that only contains float values, we can easily convert it to an int
print(atR)
