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
                "volume": item["volume"],
                "exchange": item["exchange"]
            }
            for item in data
        ]
    except Exception as e:
        return {"error": str(e)}

def search_fmp_ticker(query, limit=10):
    url = f"https://financialmodelingprep.com/api/v3/search?query={query}&limit={limit}&apikey={FINANCIAL_MODELING_PREP_KEY}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        if not data:
            return {"error": "No tickers found for the given query."}
        return data
    except Exception as e:
        return {"error": str(e)}

def get_fmp_company_profile(ticker):
    url = f"https://financialmodelingprep.com/api/v3/profile/{ticker}?apikey={FINANCIAL_MODELING_PREP_KEY}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        if not data:
            return {"error": "No profile found for the given ticker."}
        return data[0]  
    except Exception as e:
        return {"error": str(e)}

@market_bp.route('/market_data', methods=['GET', 'POST'])
def market_data():
    data = None
    error = None
    profile = None

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
                profile = get_fmp_company_profile(ticker)
            else:
                error = "Invalid data source selected."

            if isinstance(data, dict) and "error" in data:
                error = data["error"]
            if isinstance(profile, dict) and "error" in profile:
                error = profile["error"]

    return render_template('market_data.html', data=data, profile=profile, error=error)

@market_bp.route('/search_ticker', methods=['GET', 'POST'])
def search_ticker():
    results = None
    error = None

    if request.method == 'POST':
        query = request.form['query']
        if not query:
            flash("Please enter a search query.", "danger")
        else:
            results = search_fmp_ticker(query)
            if isinstance(results, dict) and "error" in results:
                error = results["error"]

    return render_template('search_ticker.html', results=results, error=error)