"""
This is a little bit of a shit show

This simulator tests your indicators and whatever strategy you program in here.
Later this should be improved to test several strategies

This tracks your cash, shares, portfolio and purse
Cash = cash
shares = the number of share you have at any one point
portfolio = the value of your shares
purse = your cash+portfolio

"""

from StringIO import StringIO
import numpy as np
from scipy.stats import linregress
#from pandas.io import data, wb # becomes
import pandas as pd
pd.core.common.is_list_like = pd.api.types.is_list_like
from pandas_datareader import data, wb
import datetime
import matplotlib.pyplot as plt
import math
#Begin Date Limit (2013, 9, 14)
#End Date Limit (2018, 9, 14)

start = datetime.datetime(2013, 10, 15)
end = datetime.datetime(2018, 12, 31) 

stockDataPath = 'C:\\Users\\adamm\\Desktop\\StockData\\'
stocks = open('C:\\Users\\adamm\\Desktop\\companylist.csv').readlines()#.split('\n')#.split(',')

singleStockStrat = False

indexToTest = 'AAPL'#Target stock
daysPrior = 5
startSale = 'open'
endSale = 'close'

posCors = ['EEFT', 'STMP']#Possitively Hitmiss correlated indicators
negCors = ['RING']#negatively hitmiss correlated indicators

#########################################################################################################


startDefault = start
endDefault = end
a = end-start
days = a.days
stockSym = []
stockSymbols = []
tick = 0
numStocks = 0


pcData = []
ncData = []

path = stockDataPath+indexToTest+'.csv'
try:
    stockData = pd.read_csv(path)
except:
    print path+" not found"
    
for i in range(len(posCors)):
    pc = posCors[i]
    path = stockDataPath+pc+'.csv'
    print path
    try:
        s = pd.read_csv(path)
        pcData.append(s) #to get 1 value example = stockData[0]['open'][0]
    except:
        print path+" not found"
        
for i in range(len(negCors)):
    nc = negCors[i]
    path = stockDataPath+nc+'.csv'
    print path
    try:
        s = pd.read_csv(path)
        ncData.append(s) #to get 1 value example = stockData[0]['open'][0]
    except:
        print path+" not found"

#ind = stockSymbols.index(indexToTest)
targetData = stockData#[ind]
targetSlope = []
indicatorSlopeTemp = []
buySellHold = []
csh = []
shrs = []
prtflo = []
purse = []
end = start
dd = daysPrior
end += datetime.timedelta(days=dd)
daysSkipped = 0
dayAssessed = []
dateForData = []
priceOpen = []
priceClose = []
portfolio = 0
shares = 0
cash = 1000
trend = 0

def buy(price,sharesTB):
    print "Buy"
    global cash
    global shares
    global portfolio
    if sharesTB == 9999:
        shares += math.trunc(cash/price)
        cash -= shares*price
        portfolio += shares*price
    else:
        shares += shareTB
        cash -= shares*price
        portfolio += shares*price
        
def sell(price,sharesTS):
    print "Sell"
    global cash
    global shares
    global portfolio
    if sharesTS == 9999:
        shares = 0
        cash += portfolio
        portfolio=0
    else:
        shares -= sharesTS
        cash += sharesTS*price
        portfolio -= sharesTS*price


if singleStockStrat: # 1st test strategy just using 1 stock
    for d in range(days):
        mask = (targetData['date'] > str(start)) & (targetData['date'] <= str(end))
        dataInRange = targetData[endSale][mask]
        x = np.arange(len(dataInRange))
        if len(dataInRange) > 1:
            slope = linregress(x,dataInRange)[0]
            targetSlope.append(slope)
            dayAssessed.append(end)
        else:
            daysSkipped += 1
        end += datetime.timedelta(days=1)
        start += datetime.timedelta(days=1)
        #print d,dd,start,end,slope
    start = startDefault
    t = 0

    firstBuy = 0
    it = 1
    p = []
    for d in range(days):
        st = start
        st += datetime.timedelta(days=1)
        mask = (targetData['date'] > str(start)) & (targetData['date'] < str(st))
        sharePrice = targetData[startSale][mask]
        
        if start in dayAssessed and len(sharePrice)>0: 
            portfolio = shares*sharePrice[it]
            #st = start
            #st += datetime.timedelta(days=2)
            #mask = (targetData['date'] > str(start)) & (targetData['date'] < str(st))
            #sharePrice = targetData[startSale][mask]
            
            if targetSlope[t] > 0:
                if firstBuy == 0:
                    shares += math.trunc(cash/sharePrice[it])
                    cash -= shares*sharePrice[it]
                    portfolio += shares*sharePrice[it]
                    firstBuy += 1
                else:
                    if cash > sharePrice[it]:
                        shares += math.trunc(cash/sharePrice[it])
                        cash -= shares*sharePrice[it]
                        portfolio += shares*sharePrice[it]
            else:
                shares = 0
                cash += portfolio
                portfolio=0
            t += 1
            print d,t,targetSlope[t],cash,shares,portfolio, cash+portfolio
            p.append(cash+portfolio)
    
        if len(mask[mask == True]) >0:
            it += 1
        start += datetime.timedelta(days=1)
    print shares, cash, portfolio
else:
    #In this strategy we test the indicators and if the majority say the target will go up then we buy as much as we can
    #If the majority say it will decrease we sell everything
    #After each desicion we wait 5 days because that is what we used in the indicator analysis
    #When we are not waiting we are testing to buy or sell
    for d in range(days):
        dateForData.append(targetData.iloc[i]['date'])
        priceOpen.append(targetData.iloc[i]['open'])
        priceClose.append(targetData.iloc[i]['close'])
    dateForData = pd.to_datetime(dateForData)
        
    start = startDefault
    t = 0
    
    firstBuy = 0
    it = 1
    p = []
    xp = np.arange(daysPrior)
    daysToWait = 0
    for d in range(daysPrior,days):
        trend = 0
        dt = pd.to_datetime(targetData.iloc[d]['date'])
        sharePrice = targetData.iloc[d]['open']
        
        if daysToWait > 0:
            daysToWait -= 1
        if daysToWait == 0:
            for p in range(len(posCors)):
                df = pd.to_datetime(pcData[p]['date'])
                mask = df.isin([dt])
                idx = [i for i, x in enumerate(mask) if x]#index of date in indicator data
                arr = pcData[p].iloc[d-daysPrior:d]['open']
                pa,intercept,rvalue,pvalue,stderr  = linregress(xp,arr)
                pa = pa/abs(pa)
                trend += pa
            for p in range(len(negCors)):
                df = pd.to_datetime(ncData[p]['date'])
                mask = df.isin([dt])
                idx = [i for i, x in enumerate(mask) if x]#index of date in indicator data
                arr = ncData[p].iloc[d-daysPrior:d]['open']
                pa,intercept,rvalue,pvalue,stderr  = linregress(xp,arr)
                pa = (pa/abs(pa))*-1
                trend += pa
            if trend > 0 and cash > sharePrice:
                buy(sharePrice,9999)
                daysToWait = 5
                buySellHold.append(1)
            elif trend < 0 and cash > sharePrice:
                daysToWait = 5
                sell(sharePrice,9999)
                buySellHold.append(-1)
            else:
                buySellHold.append(0)
        elif daysToWait > 0:
            buySellHold.append(0)
        portfolio = sharePrice*shares
        print cash+portfolio, cash, portfolio, shares, sharePrice, trend, dt
        csh.append(cash)
        shrs.append(shares)
        prtflo.append(portfolio)
        purse.append(cash+portfolio)
        