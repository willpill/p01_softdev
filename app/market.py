import requests
from flask import Blueprint, render_template, request, flash
import keys
from auth_utils import login_required
market_bp = Blueprint('market_bp', __name__)

MARKETSTACK_KEY = "3640fcf307bd1020090b38674dbaeceb"#keys.get_key("keys_marketstack.txt")
FINANCIAL_MODELING_PREP_KEY = "rWxIWYGGtVaL8WBpShqPg4LFn9W1ISUJ"#keys.get_key("keys_financialmodelingprep.txt")

def get_marketstack_eod(ticker, date_from=None, date_to=None):
    if not date_from and not date_to:
        base_url = f"http://api.marketstack.com/v1/eod/latest"
        params = {
            "access_key": MARKETSTACK_KEY,
            "symbols": ticker
        }
    else:
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
@login_required
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

def get_popular_stocks():
    url = f"https://financialmodelingprep.com/api/v3/stock_market/actives?apikey={FINANCIAL_MODELING_PREP_KEY}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        if not data:
            return {"error": "No popular stocks data found."}
        return data[:10]  
    except Exception as e:
        return {"error": str(e)}

@market_bp.route('/popular_stocks')
@login_required
def popular_stocks():
    data = get_popular_stocks()
    error = None

    if isinstance(data, dict) and "error" in data:
        error = data["error"]

    return render_template('popular_stocks.html', data=data, error=error)

@market_bp.route('/stock/<symbol>')
@login_required
def stock_detail(symbol):
    try:
        response = requests.get(f"http://api.marketstack.com/v1/eod/latest?access_key={MARKETSTACK_KEY}&symbols={symbol}")
        response.raise_for_status()
        stock_data = response.json()['data'][0]

        return render_template('stock_detail.html', stock=stock_data)
    except Exception as e:
        return f"Error fetching stock data: {e}"