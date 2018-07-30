## Computing Option Greeks

# Load the required modules and packages
from blackScholesCalculator import Black_scholes_calculator
from bs4 import BeautifulSoup
from collections import Counter
from niftyStockPrice import Nifty_stock_price
import datetime as dt
import logging
import numpy as np
import pandas as pd
import pandas_datareader.data as web
import requests

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# RBI 91 day treasury bill rate
rbi_interest_rate = 0.0652  
symbol = 'GLENMARK'
expiry_date = '28JUN2018'


# Return the number of days until expiration
def get_days_until_expiration():
    expry = dt.datetime.strptime(expiry_date, "%d%b%Y")
    today = dt.datetime.today()
    t = (expry - today).days + 1
    return float(t/365)
        

def get_options_columns(opt_table):

    col_list = []
    table_head = opt_table.find('thead')
    try:
        rows = table_head.find_all('tr')
        for tr in rows:
            cols = tr.find_all('th')
            for th in cols:
                col_list.append(th.text)
    except:
        logging.info('No Head')
    
    return [e for e in col_list if e not in ('CALLS','PUTS','Chart','\xc2\xa0','\xa0')]


def prepare_options_table(options_table_frame, table_rows):
    
    row_marker = 0
    for row_number, tr_nos in enumerate(table_rows):
        # This will ensure that we fetch only those rows which we require
        if row_number <= 1 or row_number == len(table_rows)-1:
            continue
        
        td_columns = tr_nos.find_all('td') 
        select_cols = td_columns[1:22] # This will remove unwanted columns
        for nu, column in enumerate(select_cols):
            options_table_frame.ix[row_marker, [nu]] = column.get_text()
            anchors = column.find_all('a')
            for anchor in anchors:
                options_table_frame.ix[row_marker, [nu]] = anchor.get_text()
        row_marker += 1
    

def rename_option_table_columns(col_list_fnl):
    # Counter counts the number of occurrences of each item
    counts = Counter(col_list_fnl) 
    for s, num in counts.items():
        if num > 1: # ignore strings that only appear once
            for suffix in range(1, num + 1): # suffix starts at 1 and increases by 1 each time
                col_list_fnl[col_list_fnl.index(s)] = s + str(suffix) # replace each appearance of s
    

def remove_unwanted_cols(options_table_frame):    
    options_table_frame.reset_index(inplace=True)
    del options_table_frame['time_to_expiry']
    del options_table_frame['rate_of_interest']
    del options_table_frame['underlying_prc']
    del options_table_frame['BidQty1']
    del options_table_frame['BidPrice1']
    del options_table_frame['AskPrice1']
    del options_table_frame['AskQty1']
    del options_table_frame['BidQty2']
    del options_table_frame['BidPrice2']
    del options_table_frame['AskPrice2']
    del options_table_frame['AskQty2'] 
    del options_table_frame['index'] 
    
    
def calculate_option_greeks(options_table_frame):
    underlying_price = Nifty_stock_price.stock_price(symbol)
    stk_price = underlying_price[0]
    options_table_frame['time_to_expiry'] = get_days_until_expiration()
    options_table_frame['rate_of_interest'] = rbi_interest_rate 
    options_table_frame['underlying_prc'] = stk_price
    options_table_frame['Call Delta'] = options_table_frame.apply(Black_scholes_calculator.call_delta, axis=1)
    options_table_frame['Put Delta'] = options_table_frame.apply(Black_scholes_calculator.put_delta, axis=1) 
    options_table_frame['Call Theta'] = options_table_frame.apply(Black_scholes_calculator.call_theta, axis=1)
    options_table_frame['Put Theta'] = options_table_frame.apply(Black_scholes_calculator.put_theta, axis=1) 
    options_table_frame['Call Vega'] = options_table_frame.apply(Black_scholes_calculator.vega, axis=1)
    remove_unwanted_cols(options_table_frame)
    

def export_options_table_to_csv(options_table_frame):
    options_table_frame.to_csv('Option_Chain.csv')  


try:
    logging.info(">>>>>>>>>>>>> Fetching live options data from the NSE site for the given symbol-%s & date-%s combination and then exporting the same to a CSV file.", symbol, expiry_date)
    
    # https://www.nseindia.com/live_market/dynaContent/live_watch/derivative_stock_watch.htm
    base_url = ('https://nseindia.com/live_market/dynaContent/live_watch/option_chain/optionKeys.jsp?segmentLink=17&instrument=OPTSTK&symbol='+symbol+'&date='+expiry_date)
    page = requests.get(base_url)
    soup = BeautifulSoup(page.content, 'html.parser')
    
    logging.info("Fetching the list of columns we are interested in.")
    options_table = soup.find(id="octable")
    col_list_fnl = get_options_columns(options_table)
    rename_option_table_columns(col_list_fnl)
    
    logging.info("Preparing the initial column-based structure of the options data table.")
    table_rows = options_table.find_all('tr')
    options_table_frame = pd.DataFrame(index=range(0, len(table_rows)-3), columns=col_list_fnl)
    
    logging.info("Preparing the actual structure of the options data table by setting row data.")
    prepare_options_table(options_table_frame, table_rows)        
    logging.info(options_table_frame)
    
    logging.info("Calculate Greeks for each strike price")
    calculate_option_greeks(options_table_frame)
        
    logging.info("Exporting the prepared table into a CSV file and printing it on console.")
    export_options_table_to_csv(options_table_frame)
    
    logging.info("Finished fetching live options data from the NSE site for the given symbol-%s & date-%s combination and then exporting the same to a CSV file - END", symbol, expiry_date)
    
except Exception as e:
    print('An exception occurred while fetching latest option chain for symbol:', symbol)    
    raise e
    
