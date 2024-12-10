import keys 
import urllib.request
import json
hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64)' }

currency_key = keys.get_key("keys_currencylayer.txt")
marketstack_key = keys.get_key("keys_marketstack.txt")
marketstack_key = "3640fcf307bd1020090b38674dbaeceb"
# returns either the value of the currency after conversion or none if API raises an error
def convert_currency(n, initial, end):
    try:    
        page = urllib.request.urlopen(f"https://api.currencylayer.com/convert?access_key={currency_key}&from={initial}&to={end}&amount={n}")    
        data = json.loads(page.read())
        return data["result"]
    except:
        return None

# returns a 
def get_stock(symbol):
#    print(f"https://api.marketstack.com/v1/eod?access_key={marketstack_key}&symbols={symbol}")
    try:
        r = urllib.request.Request(f"https://api.marketstack.com/v1/eod?access_key={marketstack_key}&symbols={symbol}", headers=hdr)
        page = urllib.request.urlopen(r)

        data = json.loads(page.read())
        for d in data["data"]:
            print(d)
        return data["data"][0]
    except:
        return None
print(get_stock("AAPL"))

