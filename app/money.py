import keys 
import urllib.request
import json
hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64)' }

currency_key = keys.get_key("keys_currencylayer.txt")
currency_key = "a6bc55e4910ba85a6b590df72c94b1b7"
marketstack_key = keys.get_key("keys_marketstack.txt")
marketstack_key = "3640fcf307bd1020090b38674dbaeceb"
fprep_key = "rWxIWYGGtVaL8WBpShqPg4LFn9W1ISUJ"
# note f prep is MUCH nicer than
# returns either the value of the currency after conversion or none if API raises an error
def convert_currency(n, initial, end):
    try:    
        page = urllib.request.urlopen(f"https://api.currencylayer.com/convert?access_key={currency_key}&from={initial}&to={end}&amount={n}")    
        data = json.loads(page.read())
        return data["result"]
    except:

        return None

# returns a dictionary containing most recent stock information
def get_stock(symbol):
    print(f"https://financialmodelingprep.com/api/v3/quote/{symbol}?apikey={fprep_key}")
    try:
        r = urllib.request.Request(f"https://financialmodelingprep.com/api/v3/quote/{symbol}?apikey={fprep_key}", headers=hdr)
        page = urllib.request.urlopen(r)
        data = json.loads(page.read())
        return data[0]
    except:
        return None

#def insert_stock(conn, symbol):
#    stock_info = get_stock(symbol)
#    if stock_info:
#            conn.execute(
#                'INSERT INTO stocks (stock_name, ticker_symbol, price) VALUES (?, ?, ?)',
#                (username, email, password_hash))
#            conn.commit()
print(get_stock("AAPL"))

