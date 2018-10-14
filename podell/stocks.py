"""
This just downloads all of the stock data from all of the stocks in companylist.csv 

If you find a stock online that is not in the list, just add it and rerun this script

Note: only 5 years data from now is available for free so you will have to adjust the start and end dates
"""

#from StringIO import StringIO
import numpy as np
import os
#from pandas.io import data, wb # becomes
import pandas as pd
pd.core.common.is_list_like = pd.api.types.is_list_like
#from pandas_datareader import data, wb
import datetime
start = datetime.datetime(2013, 9, 14) #edit this to be 5 years before today
end = datetime.datetime(2018, 9, 14) #make this today (yes there is a better way to do this)



outputDirectoryPath = os.path.abspath(os.path.dirname(__file__) + os.sep + '..' +  os.sep + 'stock_data')  # directory where all of the individual stock data will sit
companyListPath = outputDirectoryPath + os.sep + 'companylist.csv'  # path to the list of stock symbols


#####################################################################

stocks = open(companyListPath).readlines()
stockSym = []
stockSymbol = []
tick = 0
for l in stocks:
    if tick > 0:
        stockSym.append(l.split(',')[0].strip())
    else:
        tick += 1
begin = 0

for st in stockSym:
        try:
            f = data.DataReader(st, 'iex', start, end)
            path = outputDirectoryPath+st+'.csv'
            f.to_csv(path)
        except:
            print(st)

