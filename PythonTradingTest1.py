# -*- coding: utf-8 -*-
"""
Created on Thu Jul  2 12:06:26 2020

@author: Kaleb Dickerson
"""
#Important: Program not set up to use volume yet
import os
import time
import pandas as pd
from yahoo_fin import stock_info as si
from twilio.rest import Client
client = Client('AC861cc4c3814f460d1edd13fb4b424db4','d6f362e7e450c595ad9e720cdd9cb156')

#Initialized CSV file with account value
AccountVal = 1000
with open('Day1Test.csv','w') as MyFile:
    MyFile.write('Starting Value,'+str(AccountVal)+'\n')


#Returns the moving average from the last 50 and 10 data points
def BuyOrSell(PL,x,y,HaveStock):
    #Finding Longterm Moving Average
    PriceListTemp = PL[-x:]
    window_size = x
    Price_series = pd.Series(PriceListTemp)
    windows = Price_series.rolling(window_size)
    moving_averages = windows.mean()
    
    moving_averages_list = moving_averages.tolist()
    FAvg = moving_averages_list[window_size - 1:][0]
    #Finding Shortterm Moving Average
    PriceListTemp = PL[-y:]
    window_size = y
    
    Price_series = pd.Series(PriceListTemp)
    windows = Price_series.rolling(window_size)
    moving_averages = windows.mean()
    
    moving_averages_list = moving_averages.tolist()
    TAvg = moving_averages_list[window_size - 1:][0]
    #Deciding Weather to buy or sell
    Ratio = FAvg / TAvg
    if Ratio > 1.0001 and HaveStock == False:
        Buy = True
        Sell = False
    elif Ratio < 0.9999 and HaveStock == True:
        Sell = True
        Buy = False
    else:
        Sell = False
        Buy = False
    return Buy,Sell

#Getting the current time
t = time.localtime()
current_time = time.strftime("%H:%M:%S", t)
#Setting the ticker (only 1 allowed currently)
ticker = 'KO'
rate = 5 #seconds
#Initializing 
PriceList = []
Count = 0
Buy = False
Sell = False
HaveStock = False
LMA_Length = 5
SMA_Length = 2
#Runs continuously until 5 minutes before market closes
while current_time[:5] != '14:55':
    t = time.localtime()
    current_time = time.strftime("%H:%M:%S", t)
    #Getting current price and volume of stock and appending it to a list
    price = round(si.get_live_price(ticker),2)
    PriceList.append(price)
    #Must first collect 50 data points to construct a moving average without executing any trades
    if Count >= LMA_Length:
        #Ratio of the moving average of the most recent 10 points versus the most recent 50
        Buy, Sell = BuyOrSell(PriceList,LMA_Length,SMA_Length,HaveStock)
        #Initiates Buy and writes it to a file. Also modifies Account Value
        if Buy == True:
            print('Bought')
            HaveStock = True
            PriceBought = price
            NumShares = AccountVal // PriceBought
            AccountVal = AccountVal - (NumShares * PriceBought)
            with open('Day1Test.csv','a') as MyFile:
                ToWrite = 'BOUGHT,'+str(NumShares)+','+str(PriceBought)+','+current_time+'\n'
                MyFile.write(ToWrite)
            client.messages.create(to="+15128011561",from_="+12058915786",body=ToWrite)
        #Initiates Sell and writes it to a file. Also modifies Account Value
        if Sell == True:
            print('Sold')
            HaveStock = False
            PriceSold = price
            AccountVal = AccountVal + (NumShares * PriceSold)
            with open('Day1Test.csv','a') as MyFile:
                ToWrite = 'SOLD,'+str(NumShares)+','+str(PriceSold)+','+current_time+'\n'
                MyFile.write(ToWrite)
            client.messages.create(to="+15128011561",from_="+12058915786",body=ToWrite)
            
    
    Count += 1
    #Delays the program for 'rate' seconds
    time.sleep(rate)
    current_time = time.strftime("%H:%M:%S", t)
#Writes the final Account Value to the CSV file
with open('Day1Test.csv','a') as MyFile:
    MyFile.write('Ending Value,'+str(AccountVal)+'\n')
client.messages.create(to="+15128011561",from_="+12058915786",body='Final Value = '+str(AccountVal))
os.system("shutdown /s /t 1")

