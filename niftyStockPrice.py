from urllib.request import Request, urlopen
import re

class Nifty_stock_price:
    
    def stock_price(stock):
        hdr = {'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.107 Safari/537.36',
                            'Upgrade-Insecure-Requests': '1',
                            'x-runtime': '148ms'}
        
        req = Request('https://www.nseindia.com/live_market/dynaContent/live_watch/get_quote/GetQuote.jsp?symbol='+stock, headers=hdr)
        nav = urlopen(req)
        data = nav.read()
        
        srch = '"lastPrice":"(.+?)"' 
        com = re.compile(srch)
        rslt = re.findall(com, str(data))
        return rslt  