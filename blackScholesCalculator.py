from scipy.stats import norm
from niftyStockPrice import Nifty_stock_price
import datetime as dt
import numpy as np

class Black_scholes_calculator:
    
    # Normal cumulative density function
    def N(z):
        return norm.cdf(z, 0.0, 1.0)

    # Calculate call option value
    def calculate_call_value(options_table_frame):
        S = float(options_table_frame['underlying_prc'])
        K = float(options_table_frame['Strike Price'])  
        vol = options_table_frame['IV1']
        r = float(options_table_frame['rate_of_interest'])
        t = float(options_table_frame['time_to_expiry'])
        vol = 0.0 if vol.strip() == '-' else float(vol)/100
            
        d1 = (np.log(S / K) + (r + 0.5 * vol ** 2) * t) / (vol * np.sqrt(t)) 
        d2 = (np.log(S / K) + (r - 0.5 * vol ** 2) * t) / (vol * np.sqrt(t)) 
        return (S * norm.cdf(d1, 0.0, 1.0) - K * np.exp(-r * t) * norm.cdf(d2, 0.0, 1.0))
        
    # Calculate put option value
    def calculate_put_value(options_table_frame):
        S = float(options_table_frame['underlying_prc'])
        K = float(options_table_frame['Strike Price'])  
        vol = options_table_frame['IV2']
        r = float(options_table_frame['rate_of_interest'])
        t = float(options_table_frame['time_to_expiry'])
        vol = 0.0 if vol.strip() == '-' else float(vol)/100
        
        d1 = (np.log(S / K) + (r + 0.5 * vol ** 2) * t) / (vol * np.sqrt(t)) 
        d2 = (np.log(S / K) + (r - 0.5 * vol ** 2) * t) / (vol * np.sqrt(t)) 
        return norm.cdf(-d2, 0.0, 1.0) * K * np.exp(-r * t) - norm.cdf(-d1, 0.0, 1.0) * S

    # Phi helper function
    def phi(x):
        return np.exp(-0.5 * x * x) / (np.sqrt(2.0 * (3.14)))

    # Calculate Call Delta
    def call_delta(options_table_frame):
        S = float(options_table_frame['underlying_prc'])
        K = float(options_table_frame['Strike Price'])  
        vol = options_table_frame['IV1']
        r = float(options_table_frame['rate_of_interest'])
        t = float(options_table_frame['time_to_expiry'])
        vol = 0.0 if vol.strip() == '-' else float(vol)/100
        
        d1 = (1.0/(vol * np.sqrt(t))) * (np.log(S/K) + (r + 0.5 * vol**2.0) * t)
        return norm.cdf(d1, 0.0, 1.0)

    # Calculate Put Delta     
    def put_delta(options_table_frame):
        S = float(options_table_frame['underlying_prc'])
        K = float(options_table_frame['Strike Price'])  
        vol = options_table_frame['IV2']
        r = float(options_table_frame['rate_of_interest'])
        t = float(options_table_frame['time_to_expiry'])
        vol = 0.0 if vol.strip() == '-' else float(vol)/100
        
        d1 = (1.0/(vol * np.sqrt(t))) * (np.log(S/K) + (r + 0.5 * vol**2.0) * t)
        return norm.cdf(d1, 0.0, 1.0) - 1.0
    
    # Calculate Vega
    def vega(options_table_frame):
        S = float(options_table_frame['underlying_prc'])
        K = float(options_table_frame['Strike Price'])  
        vol = options_table_frame['IV1']
        r = float(options_table_frame['rate_of_interest'])
        t = float(options_table_frame['time_to_expiry'])
        vol = 0.0 if vol.strip() == '-' else float(vol)/100
        
        d1 = (1.0/(vol * np.sqrt(t))) * (np.log(S/K) + (r + 0.5 * vol**2.0) * t)
        return (S * Black_scholes_calculator.phi(d1) * np.sqrt(t)) / 100.0
    
    # Calculate Call Theta
    def call_theta(options_table_frame):
        S = float(options_table_frame['underlying_prc'])
        K = float(options_table_frame['Strike Price'])  
        vol = options_table_frame['IV1']
        r = float(options_table_frame['rate_of_interest'])
        t = float(options_table_frame['time_to_expiry'])
        vol = 0.0 if vol.strip() == '-' else float(vol)/100
        
        d1 = (1.0/(vol * np.sqrt(t))) * (np.log(S/K) + (r + 0.5 * vol**2.0) * t)
        d2 = d1 - (vol * np.sqrt(t))
        theta = -((S * Black_scholes_calculator.phi(d1) * vol) / (2.0 * np.sqrt(t))) - (r * K * np.exp(-r * t) * norm.cdf(d2, 0.0, 1.0))
        return theta / 365.0
    
    # Calculate Put Theta
    def put_theta(options_table_frame):
        S = float(options_table_frame['underlying_prc'])
        K = float(options_table_frame['Strike Price'])  
        vol = options_table_frame['IV2']
        r = float(options_table_frame['rate_of_interest'])
        t = float(options_table_frame['time_to_expiry'])
        vol = 0.0 if vol.strip() == '-' else float(vol)/100
        
        d1 = (1.0/(vol * np.sqrt(t))) * (np.log(S/K) + (r + 0.5 * vol**2.0) * t)
        d2 = d1 - (vol * np.sqrt(t))
        theta = -((S * Black_scholes_calculator.phi(d1) * vol) / (2.0 * np.sqrt(t))) + (r * K * np.exp(-r * t) * norm.cdf(-d2, 0.0, 1.0))
        return theta / 365.0
    
    # Calculate Gamma
    def gamma(options_table_frame):
        S = float(options_table_frame['underlying_prc'])
        K = float(options_table_frame['Strike Price'])  
        vol = options_table_frame['IV2']
        r = float(options_table_frame['rate_of_interest'])
        t = float(options_table_frame['time_to_expiry'])
        vol = 0.0 if vol.strip() == '-' else float(vol)/100
        
        d1 = (1.0/(vol * np.sqrt(t))) * (np.log(S/K) + (r + 0.5 * vol**2.0) * t)
        return Black_scholes_calculator.phi(d1) / (S * vol * np.sqrt(t))
    