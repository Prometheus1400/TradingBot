# -*- coding: utf-8 -*-
"""
Created on Sun Jul  5 10:17:27 2020

@author: Kaleb Dickerson
"""
import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt
plt.rcParams["figure.figsize"] = (20,20)

with open('BACKTEST.csv','w') as MyFile:
    MyFile.write('')
#Returns the moving average from the last 50 and 10 data points
def Past25Avg(PL_1):
    PriceListTemp = PL_1[-15:]
    window_size = 15
    Price_series = pd.Series(PriceListTemp)
    windows = Price_series.rolling(window_size)
    moving_averages = windows.mean()
    
    moving_averages_list = moving_averages.tolist()
    FAvg = moving_averages_list[window_size - 1:][0]
    
    return FAvg
def Past10Avg(PL_2):
    PriceListTemp = PL_2[-5:]
    window_size = 5
    
    Price_series = pd.Series(PriceListTemp)
    windows = Price_series.rolling(window_size)
    moving_averages = windows.mean()
    
    moving_averages_list = moving_averages.tolist()
    TAvg = moving_averages_list[window_size - 1:][0]
    
    return TAvg

AccountVal = 1000

Apple = yf.Ticker('AAPL')
Hist = Apple.history(interval='1m',start='2020-07-01',end='2020-07-02')
PriceList = []
Count = 0
Buy = False
Sell = False
HaveStock = False
while Count < len(Hist):
    price = Hist['Close'][Count]
    PriceList.append(price)
    #Must first collect 25 data points to construct a moving average without executing any trades
    if Count >= 25:
        #Ratio of the moving average of the most recent 10 points versus the most recent 50
        TwentyFive = Past25Avg(PriceList)
        Ten = Past10Avg(PriceList)
        Ratio = Ten / TwentyFive

        if Ratio > 1.0001 and HaveStock == False:
            Buy = True
            Sell = False
        elif Ratio < 0.9999 and HaveStock == True:
            Sell = True
            Buy = False
        else:
            Buy = False
            Sell = False
        #Initiates Buy and writes it to a file. Also modifies Account Value
        if Buy == True:
            print('Bought')
            HaveStock = True
            PriceBought = price
            NumShares = AccountVal // PriceBought
            AccountVal = AccountVal - (NumShares * PriceBought)
            with open('BACKTEST.csv','a') as MyFile:
                MyFile.write('BOUGHT,'+str(NumShares)+','+str(PriceBought)+','+'\n')
        #Initiates Sell and writes it to a file. Also modifies Account Value
        elif Sell == True:
            print('Sold')
            HaveStock = False
            PriceSold = price
            AccountVal = AccountVal + (NumShares * PriceSold)
            with open('BACKTEST.csv','a') as MyFile:
                MyFile.write('SOLD,'+str(NumShares)+','+str(PriceSold)+','+'\n')
    Count += 1
with open('BACKTEST.csv','a') as MyFile:
    MyFile.write('Ending Value,'+str(AccountVal)+'\n')
    
if HaveStock == False:
    print('Final Value: ',AccountVal)
elif HaveStock == True:
    print('Final Value: ',AccountVal + NumShares*PriceSold)
    

