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
        return response.json().get("data", [])
    except Exception as e:
        return {"error": str(e)}

def get_financialmodelingprep_quote(ticker):
    url = f"https://financialmodelingprep.com/api/v3/quote/{ticker}?apikey={FINANCIAL_MODELING_PREP_KEY}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
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
