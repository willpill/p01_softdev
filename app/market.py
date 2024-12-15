import requests
from flask import Blueprint, render_template, request, flash
import keys

market_bp = Blueprint('market_bp', __name__)

MARKETSTACK_KEY = "3640fcf307bd1020090b38674dbaeceb"#keys.get_key("keys_marketstack.txt")
FINANCIAL_MODELING_PREP_KEY = "rWxIWYGGtVaL8WBpShqPg4LFn9W1ISUJ"#keys.get_key("keys_financialmodelingprep.txt")

def get_marketstack_eod(ticker, date_from=None, date_to=None):
    base_url = "http://api.marketstack.com/v1/eod"
    params = {
        "access_key": MARKETSTACK_KEY,
        "symbols": ticker,
        "date_from": date_from,
        "date_to": date_to,
    }
    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        data = response.json().get("data", [])
        if not data:
            return {"error": "No data found for the given ticker and date range."}

        return [
            {
                "symbol": item["symbol"],
                "date": item["date"],
                "open": item["open"],
                "high": item["high"],
                "low": item["low"],
                "close": item["close"],
                "volume": item["volume"]
            }
            for item in data
        ]
    except Exception as e:
        return {"error": str(e)}

def get_financialmodelingprep_quote(ticker):
    url = f"https://financialmodelingprep.com/api/v3/quote/{ticker}?apikey={FINANCIAL_MODELING_PREP_KEY}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        if not data:
            return {"error": "No data found for the given ticker."}

        # Extract relevant fields
        return [
            {
                "symbol": item["symbol"],
                "price": item["price"],
                "open": item["open"],
                "high": item["dayHigh"],
                "low": item["dayLow"],
                "previous_close": item["previousClose"],
                "volume": item["volume"]
            }
            for item in data
        ]
    except Exception as e:
        return {"error": str(e)}

@market_bp.route('/market_data', methods=['GET', 'POST'])
def market_data():
    data = None
    error = None

    if request.method == 'POST':
        ticker = request.form['ticker'].upper()
        source = request.form['source']
        date_from = request.form.get('date_from')
        date_to = request.form.get('date_to')

        if not ticker:
            flash("Please enter a ticker symbol.", "danger")
        else:
            if source == 'marketstack':
                data = get_marketstack_eod(ticker, date_from, date_to)
            elif source == 'financialmodelingprep':
                data = get_financialmodelingprep_quote(ticker)
            else:
                error = "Invalid data source selected."

            if isinstance(data, dict) and "error" in data:
                error = data["error"]

    return render_template('market_data.html', data=data, error=error)