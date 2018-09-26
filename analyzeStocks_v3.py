"""
This finds indicator stocks that correlate with our target stock.
The inicator stocks will then go into the stockSimulator to test whatever strategy you code in there
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
#Begin Date Limit (2013, 9, 14)
#End Date Limit (2018, 9, 14)

stockDataPath = 'C:\\Users\\adamm\\Desktop\\StockData\\' #path to stock data directory
stocks = open('C:\\Users\\adamm\\Desktop\\companylist.csv').readlines() # company list

indexToTest = 'AAPL' #target stock

daysPast = 5 # the number of days that will get tested together before target date
daysFuture = 5 # the number of days that will occur after the target date that will be correlated to

days = 300 #number of days that will be used to find the indicator stocks

justTestOne = False #This isn't used anymore. Just leave false. I will remove all that stuff

################################################################################################################

stockSym = []
stockSymbols = []
allRValues = []
tick = 0
numStocks = 0

#Read stock list
for l in stocks:
    if tick > 0:
        stockSym.append(l.split(',')[0].strip())
        numStocks += 1
    else:
        tick += 1

#Load stock data into memory
stockData = []
if justTestOne: #ignore
    path = stockDataPath+indexToTest+'.csv'
    print path
    try:
        s = pd.read_csv(path)
        stockData.append(s) #to get 1 value example = stockData[0]['open'][0]
        stockSymbols.append(indexToTest)
    except:
        print path+" not found"
        try:
            f = data.DataReader(indexToTest, 'iex', start, end)
            path1 = 'C:\\Users\\adamm\\Desktop\\StockData\\'+st+'.csv'
            f.to_csv(path1)
        except:
                print "This is not even a stock. Do you even model bro?"
        try:
            s = pd.read_csv(path)
            stockData.append(s) #to get 1 value example = stockData[0]['open'][0]
            stockSymbols.append(indexToTest)
        except:
            print "Nothing to be done just forget this stock"
else:# load all stock data into memory
    for i in range(numStocks):
        if i%1000 == 0:
            print i, numStocks
        
        path = stockDataPath+stockSym[i]+'.csv'
        try:
            s = pd.read_csv(path)
            stockData.append(s) #to get 1 value example = stockData[0]['open'][0]
            stockSymbols.append(stockSym[i])
        except: #if a stock is in the list but we don't have its data
            print path+" not found"
            try:#try  to download the data again
                f = data.DataReader(stockSym[i], 'iex', start, end)
                path1 = 'C:\\Users\\adamm\\Desktop\\StockData\\'+stockSym[i]+'.csv'
                f.to_csv(path1)
            except:
                print "This is not even a stock. Do you even model bro?"
            try: # Do we have the data now?
                s = pd.read_csv(path)
                stockData.append(s) #to get 1 value example = stockData[0]['open'][0]
                stockSymbols.append(stockSym[i])
            except: #Fuck it
                print "Nothing to be done just forget this stock"

ind = stockSymbols.index(indexToTest) #index of our target stock in the symbols list
targetData = stockData[ind] #get the data for the index (the target stock)

price = []
date = []
fTarget = []
pTarget = []
date = []
dateForData = []
for i in range (daysPast, days):#Don't start right at the beginning so you leave a little room to get past data before target date
    xf = np.arange(daysFuture)
    xp = np.arange(daysPast)
    fut = targetData.iloc[i:i+daysFuture]['open'] #Get the opening price for all the the days from target date to the number of days in the future you specify
    pas = targetData.iloc[i-daysPast:i]['open'] #Get the number of days in data in the past that will be used as an indicator
    
    #Get some linear regression lines. I don't really care about this info anymore, but may be interesting
    pa,intercept,rvalue,pvalue,stderr  = linregress(xp,pas)
    fu,intercept,rvalue,pvalue,stderr  = linregress(xf,fut)
    fTarget.append(fu)
    pTarget.append(pa)
    price.append(targetData.iloc[i]['open'])#save price of target date. This could be removed. There is a smarter way to do this
    if i == daysPast: # if we are in the first iteration
        for a in range(daysPast):# we need to save the dates that aren't target date but we use as indicators. We use this later
            dateForData.append(targetData.iloc[a]['date']) #Save the date
    date.append(targetData.iloc[i]['date'])#Save the date. I don't know why I have this
    dateForData.append(targetData.iloc[i]['date'])# save the target date
    if i == days-1:#If its the last day
        for a in range(daysFuture):#we also need some future dates as well that aren't target dates
            dateForData.append(targetData.iloc[days+a]['date'])
    
        
#Here's part of the magic
fTarget = np.asarray(fTarget) #convert to numpy arrays
pTarget = np.asarray(pTarget)
#we don't care about the steepness of the trend slopes for the future or the past of the target stock. We only care if it is going up or down
#So just set a 1 for a positive slope and a -1 for a negative slope
fTarget[fTarget>0] = 1
fTarget[fTarget<0] = -1
pTarget[pTarget>0] = 1
pTarget[pTarget<0] = -1
#print f
dt = pd.to_datetime(dateForData)#convert dates to standard date format
ld = len(dt)
corrs = []
stks = []
hms = []
for s in range(numStocks):#for all stocks
    #Do everything pretty much the same as above but these will be indicator stocks. Note: the target stock can also be an indicator (but seems never to be strangely enough)
    try:
        ind = stockSymbols.index(stockSym[s])
        targetData = stockData[ind]
        df = pd.to_datetime(targetData['date'])
        mask = df.isin(dt)
        
        arr = targetData['open'][mask]
        if len(arr) == ld:
            fTarget2 = []
            pTarget2 = []
            for i in range (daysPast, days):
                fut = targetData.iloc[i:i+daysFuture]['open']
                pas = targetData.iloc[i-daysPast:i]['open']
                #print fut, xf, daysFuture
                pa,intercept,rvalue,pvalue,stderr  = linregress(xp,pas)
                fu,intercept,rvalue,pvalue,stderr  = linregress(xf,fut)
                fTarget2.append(fu)
                pTarget2.append(pa)
        
            fTarget2 = np.asarray(fTarget2)
            pTarget2 = np.asarray(pTarget2)
            fTarget2[fTarget2>0] = 1
            fTarget2[fTarget2<0] = -1
            pTarget2[pTarget2>0] = 1
            pTarget2[pTarget2<0] = -1
            #Now lets figure out how the indicator stock before the target date matches with the target stock after the target date
            #Hits and misses analysis. 
            #Hit = The indicator before the target stock has the same slope as the target stock after the target date
            #Miss = The have opposite slopes           
            tot = len(fTarget)
            hits = len(fTarget[(fTarget == 1) & (pTarget2==1)]) + len(fTarget[(fTarget == -1) & (pTarget2 == -1)])
            misses = len(fTarget[(fTarget == 1) & (pTarget2==-1)]) + len(fTarget[(fTarget == -1) & (pTarget2 == 1)])
            hm = (hits-misses)/float(len(fTarget))
            #hm = 0 means the indicator equaly hits and misses so we get no information from this indicator stock
            #hm = 1 means the indicator stock always has the same slope before the target date and the target stock after the target date
            #hm = -1means the indicator stock always has the opposite slope before the target date and the target stock after the target date
            #hm = .5 means same slopes 75% of the time
            hms.append(hm)
            #
            slope,intercept,rvalue,pvalue,stderr = linregress(fTarget,pTarget2)
            corrs.append(rvalue)
            stks.append(stockSym[s])
            print hm,rvalue,s,numStocks,stockSym[s]
    except:
        print stockSym[s] + ' not in list'
print("Here are your top linearly correlated indicator stocks")
mn = min(corrs)
mx = max(corrs)
print mn
print mx
ss = np.asarray(stks)
corrs = np.asarray(corrs)

mn1 = mn - mn*.1
mx1 = mx -mx*.1

crs = np.asarray(corrs)
t=crs[crs>mx1]
print t
g=np.isin(corrs,t)
gi=np.where(g)
ix=ss[gi]
print ix
t=crs[crs<mn1]
print t
g=np.isin(corrs,t)
gi=np.where(g)
ix=ss[gi]
print ix
#########
print("Here are your top HitMiss correlated indicator stocks. These ones are better")
mn = min(hms)
mx = max(hms)
print mn
print mx
ss = np.asarray(stks)
corrs = np.asarray(hms)

mn1 = mn - mn*.1
mx1 = mx -mx*.1
crs = np.asarray(hms)
t=crs[crs>mx1]
print t
g=np.isin(hms,t)
gi=np.where(g)
ix=ss[gi]
print ix
t=crs[crs<mn1]
print t
g=np.isin(hms,t)
gi=np.where(g)
ix=ss[gi]
print ix

###############To get data with same dates
"""
df = pd.to_datetime(targetData['date'])
dt = pd.to_datetime(date)

mask = df.isin(dt)
arr = targetData['open'][mask]
"""

if justTestOne:
    slope,intercept,rvalue,pvalue,stderr = linregress(f,p)
    print rvalue, len(f) ,len(p),daysSkipped
    
    plt.scatter(f,p)
    plt.show()
    z = np.zeros(len(f))
    plt.plot(np.arange(len(f)),z)
    plt.plot(f, label = 'futureSlope')
    plt.plot(p, label = 'pastSlope')
    plt.legend()
    plt.show()
    plt.plot(date,price)
    plt.show()

