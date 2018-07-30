## Program for back testing the monthly trade setup strategy

# Load the required modules and packages
from blackScholesCalculator import Black_scholes_calculator
from bs4 import BeautifulSoup
from collections import Counter
from niftyStockPrice import Nifty_stock_price
from pandas.io.json import json_normalize
import datetime as dt
import json
import logging
import numpy as np
import pandas as pd
import pandas_datareader.data as web
import requests
    
                
def export_data_to_csv(main_data_frame):
    main_data_frame.to_csv('monthly_trade_setup.csv')  


def get_data(url):
    req = (url)
    res = requests.get(req)
    json_data_dict = json.loads(res.text)
    keys = list(json_data_dict.keys())
    print('Data Dictionary = ', json_data_dict)
    series = keys[1]
    return pd.DataFrame.from_dict(json_data_dict[series], orient='index')
   

def analyse_the_series(main_data_frame):
    buy_signal_issued = False
    trade_entered = False
    first_target_ach = False
    second_target_ach = False 
    first_trade_done = False
    first_target = 0.0 
    first_target_profit = 0.0
    second_target = 0.0 
    second_target_profit = 0.0
    total_profit = 0.0 
    buy_price = 0.0
    
    count = 0 
    for i, row in main_data_frame.iterrows():
        # Skip all the rows until Bollinger
        # bands data is not available
        count += 1
        if count < 21:
            continue
        
        date = row[0]
        
        open_price = float(row['1. open'])
        high_price = float(row['2. high'])
        low_price = float(row['3. low'])
        close_price = float(row['4. close'])
        prev_high = float(row['prev_high'])
        prev_low = float(row['prev_low'])
        prev_close = float(row['prev_close'])
        upper_band = float(row['UBANDS'])
        lower_band = float(row['LBANDS'])
        prev_upper_band = float(row['prev_upper_band'])
        sma = float(row['SMA'])
        rsi = row['RSI']          
        prev_sma = float(row['prev_sma'])
        prev_rsi = float(row['prev_rsi'])
        
        if buy_signal_issued and not trade_entered and (prev_close < prev_upper_band or prev_rsi < 60):
            buy_signal_issued = False
            print('Buy signal exited!', 'Previous Bollinger upper_band = ', prev_upper_band, 'Previous close price = ', prev_close, 'Previous RSI = ', prev_rsi, 'Date = ', date)
            trade_entered = False
            first_trade_done = False
            print('      ')
            print('      ')
            print('      ')
            continue
        elif buy_signal_issued and first_trade_done and prev_close < prev_sma and buy_price == 0.0:
            buy_signal_issued = False
            trade_entered = False
            first_trade_done = False
            print('Trade exited!', 'Previous close price = ', prev_close, 'Previous SMA = ', prev_sma, 'Date = ', date)
            print('      ')
            print('      ')
            print('      ')
            continue
        elif not buy_signal_issued and prev_close > prev_upper_band and prev_rsi > 60:
            buy_signal_issued = True
            print('Buy signal issued!', 'Previous Bollinger upper_band = ', prev_upper_band, 'Previous close price = ', prev_close, 'Previous RSI = ', prev_rsi, 'Date = ', date)
        
        
        if buy_signal_issued and prev_high < high_price and (not trade_entered and prev_close > prev_upper_band and prev_rsi > 60):
                buy_price = prev_high
                first_target_profit = (prev_high * 6.0) / 100
                first_target = buy_price + first_target_profit
                second_target_profit = (prev_high * 12.0) / 100
                second_target = buy_price + second_target_profit 
                trade_entered = True
                print('First trade entered. Stock bought at price = ', buy_price, ' First target = ', first_target, ' Second target = ', second_target, ' Date = ', date)
                
        if buy_signal_issued and buy_price != 0.0 and not first_trade_done:
            if first_target < high_price and not first_target_ach:
                print('First target achieved date = ', date)
                first_target_ach = True
                
            if second_target < high_price and not second_target_ach:
                print('Second target achieved date = ', date)
                second_target_ach = True
            
            if low_price < prev_low:
                if first_target_ach:
                    total_profit += first_target_profit
                if second_target_ach:
                    total_profit += second_target_profit
                if not first_target_ach and not second_target_ach:
                    total_profit = buy_price - prev_low
                elif first_target_ach and second_target_ach:
                    total_profit += (max(buy_price, prev_low) - buy_price)
                    print('Third profit = ', (max(buy_price, prev_low) - buy_price))
                print('Stop loss triggered as previous months low hit = ', prev_low, ' Low price = ', low_price ,' Total profit for the trade was = ', total_profit, ' Date = ', date)
                first_trade_done = True
                first_target_ach = False
                second_target_ach = False 
                first_target = 0.0 
                first_target_profit = 0.0
                second_target = 0.0 
                second_target_profit = 0.0
                total_profit = 0.0   
                buy_price = 0.0     
                        
        elif buy_signal_issued and first_trade_done:
            if prev_high < high_price and buy_price == 0.0:
                buy_price = prev_high
                total_profit = 0.0
                print('One more trade entered as close price is still above 6 month SMA. Stock bought at price = ', buy_price, ' Previous Close Price = ', prev_close, ' SMA = ', sma, ' Date = ', date)
            elif buy_price != 0.0 and low_price < prev_low:
                total_profit = (max(buy_price, prev_low) - buy_price)
                print('Stop loss triggered as previous months low hit = ', prev_low, ' Low price = ', low_price , ' Buy price = ', buy_price, ' Total profit for the trade was = ', total_profit, ' Date = ', date)
                total_profit = 0.0   
                buy_price = 0.0     
                
            

alpha_vantage_key = 'TH699ORCPCSJAZ7L'
symbol = 'NSE:DHFL'
time_series_url = 'https://www.alphavantage.co/query?function=TIME_SERIES_MONTHLY&symbol=' + symbol + '&apikey=' + alpha_vantage_key
bbands_url = 'https://www.alphavantage.co/query?function=BBANDS&symbol=' + symbol + '&interval=monthly&time_period=20&series_type=close&apikey=' + alpha_vantage_key
sma__url = 'https://www.alphavantage.co/query?function=SMA&symbol=' + symbol + '&interval=monthly&time_period=6&series_type=close&apikey=' + alpha_vantage_key
rsi_url = 'https://www.alphavantage.co/query?function=RSI&symbol=' + symbol + '&interval=monthly&time_period=14&series_type=close&apikey=' + alpha_vantage_key
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

    
try:
    
    logging.info(">>>>>>>>>>>>> Monthly trade setup data for stock - %s", symbol)

    logging.info("Reading main time series")
#     main_data_frame = get_data(time_series_url)
#     main_data_frame['prev_high'] = main_data_frame['2. high'].shift()   
#     main_data_frame['prev_low'] = main_data_frame['3. low'].shift()   
#        
#     logging.info("Reading Bollinger bands series")
#     bbands_frame = get_data(bbands_url)
#     main_data_frame['UBANDS'] = bbands_frame['Real Upper Band']
#     main_data_frame['LBANDS'] = bbands_frame['Real Lower Band']
#      
#     logging.info("Reading sma series")
#     sma_frame = get_data(sma__url)
#     main_data_frame['SMA'] = sma_frame['SMA']
#      
#     logging.info("Reading RSI series")
#     rsi_frame = get_data(rsi_url)
#     main_data_frame['RSI'] = rsi_frame['RSI']
#     
    #export_data_to_csv(main_data_frame)
    
    main_data_frame = pd.read_csv('monthly_trade_setup.csv')
    main_data_frame['prev_close'] = main_data_frame['4. close'].shift()
    main_data_frame['prev_upper_band'] = main_data_frame['UBANDS'].shift()
    main_data_frame['prev_sma'] = main_data_frame['SMA'].shift()
    main_data_frame['prev_rsi'] = main_data_frame['RSI'].shift()
    
    analyse_the_series(main_data_frame)
                
except Exception as e:
    print('An exception occurred while fetching latest option chain for symbol:', symbol)    
    raise e
    

#     start = dt.datetime(2018, 3, 1)
#     end = dt.datetime(2018, 6, 1)
#     TESLA = web.DataReader('TSLA', 'morningstar', start, end)
#     TESLA['Log_Ret'] = np.log(TESLA['Close'] / TESLA['Close'].shift(1))
#     print(TESLA.tail(15))
#     TESLA.plot(subplots=True, color='blue', figsize=(8, 6))

