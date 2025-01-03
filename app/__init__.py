import os
import sqlite3
import keys

from functools import wraps
import money
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash

from build_db import setup_database
from currency_exchange import currency_bp 
from market import market_bp, get_popular_stocks



app = Flask(__name__)
app.secret_key = os.urandom(24)
app.register_blueprint(currency_bp)
app.register_blueprint(market_bp)
currency_key = keys.get_key("keys_currencylayer.txt")
fixer_key = keys.get_key("keys_fixer.txt")
marketstack_key = keys.get_key("keys_marketstack.txt")
modelingprep_key = keys.get_key("keys_financialmodelingprep.txt")

def get_db_connection():
    conn = sqlite3.connect('stonks.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def home():
    if 'username' in session:
        username = session['username']
        conn = get_db_connection()
        user_data = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        conn.close()
        popular_stocks = get_popular_stocks()
        return render_template('home.html', user=user_data, popular_stocks=popular_stocks)
    else:
        popular_stocks = get_popular_stocks()
        return render_template('home.html', user=None, popular_stocks=popular_stocks)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        conn.close()
        if not user:
            flash('Username does not exist.', 'danger')
        elif not check_password_hash(user['password_hash'], password):
            flash('Incorrect password.', 'danger')
        else:
            session['username'] = username
            flash('Login successful!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('home'))
    return render_template('login.html')


@app.route('/logout', methods=['GET','POST'])
def logout():
    session.pop('username', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('home'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        password_hash = generate_password_hash(password)

        conn = get_db_connection()
        try:
            conn.execute(
                'INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)',
                (username, email, password_hash)
            )
            conn.commit()
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError as e:
            existing_user = conn.execute('SELECT * FROM users WHERE username = ? OR email = ?', (username, email)).fetchone()
            if existing_user:
                if existing_user['username'] == username:
                    flash('Username is already in use.', 'danger')
                elif existing_user['email'] == email:
                    flash('Email is already in use.', 'danger')
            else:
                flash('An unexpected error occurred.', 'danger')
        finally:
            conn.close()

    return render_template('register.html')
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            flash('You must be logged in to access this page.', 'danger')
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function
@app.route('/watchlist')
@login_required
def watchlist():
    conn = get_db_connection()
    username = session['username']
    stocks = conn.execute('SELECT * FROM watchlist WHERE username = ?', (username,)).fetchall()
    conn.close()
    return render_template('watchlist.html', stocks=stocks)

@app.route('/add_to_watchlist', methods=['POST'])
@login_required
def add_to_watchlist():
    ticker = request.form['ticker'].upper()
    username = session['username']

    if not ticker:
        flash('Please enter a valid ticker symbol.', 'danger')
        return redirect(url_for('watchlist'))

    conn = get_db_connection()
    try:
        existing_stock = conn.execute('SELECT * FROM watchlist WHERE username = ? AND ticker = ?', (username, ticker)).fetchone()
        
        if existing_stock:
            flash(f'{ticker} is already in your watchlist.', 'danger')
        else:
            conn.execute('INSERT INTO watchlist (username, ticker) VALUES (?, ?)', (username, ticker))
            conn.commit()
            flash(f'{ticker} added to your watchlist!', 'success')
    except Exception as e:
        flash(f'An error occurred: {str(e)}', 'danger')
    finally:
        conn.close()

    return redirect(url_for('watchlist'))


@app.route('/remove_from_watchlist/<int:stock_id>', methods=['POST'])
@login_required
def remove_from_watchlist(stock_id):
    conn = get_db_connection()
    conn.execute('DELETE FROM watchlist WHERE id = ?', (stock_id,))
    conn.commit()
    conn.close()
    flash('Stock removed from your watchlist.', 'success')
    return redirect(url_for('watchlist'))

'''CURRENCY_OPTIONS = """
<option value='AED' title='United Arab Emirates Dirham'>AED</option>
<option value='AFN' title='Afghan Afghani'>AFN</option>
<option value='ALL' title='Albanian Lek'>ALL</option>
<option value='AMD' title='Armenian Dram'>AMD</option>
<option value='ANG' title='Netherlands Antillean Guilder'>ANG</option>
<option value='AOA' title='Angolan Kwanza'>AOA</option>
<option value='ARS' title='Argentine Peso'>ARS</option>
<option value='AUD' title='Australian Dollar'>AUD</option>
<option value='AWG' title='Aruban Florin'>AWG</option>
<option value='AZN' title='Azerbaijani Manat'>AZN</option>
<option value='BAM' title='Bosnia-Herzegovina Convertible Mark'>BAM</option>
<option value='BBD' title='Barbadian Dollar'>BBD</option>
<option value='BDT' title='Bangladeshi Taka'>BDT</option>
<option value='BGN' title='Bulgarian Lev'>BGN</option>
<option value='BHD' title='Bahraini Dinar'>BHD</option>
<option value='BIF' title='Burundian Franc'>BIF</option>
<option value='BMD' title='Bermudan Dollar'>BMD</option>
<option value='BND' title='Brunei Dollar'>BND</option>
<option value='BOB' title='Bolivian Boliviano'>BOB</option>
<option value='BRL' title='Brazilian Real'>BRL</option>
<option value='BSD' title='Bahamian Dollar'>BSD</option>
<option value='BTC' title='Bitcoin'>BTC</option>
<option value='BTN' title='Bhutanese Ngultrum'>BTN</option>
<option value='BWP' title='Botswanan Pula'>BWP</option>
<option value='BYN' title='Belarusian Ruble'>BYN</option>
<option value='BYR' title='Belarusian Ruble'>BYR</option>
<option value='BZD' title='Belize Dollar'>BZD</option>
<option value='CAD' title='Canadian Dollar'>CAD</option>
<option value='CDF' title='Congolese Franc'>CDF</option>
<option value='CHF' title='Swiss Franc'>CHF</option>
<option value='CLF' title='Chilean Unit of Account (UF)'>CLF</option>
<option value='CLP' title='Chilean Peso'>CLP</option>
<option value='CNY' title='Chinese Yuan'>CNY</option>
<option value='COP' title='Colombian Peso'>COP</option>
<option value='CRC' title='Costa Rican Colón'>CRC</option>
<option value='CUC' title='Cuba Convertible Peso'>CRC</option>
<option value='CUP' title='Cuban Peso'>CUP</option>
<option value='CVE' title='Cape Verdean Escudo'>CVE</option>
<option value='CZK' title='Czech Republic Koruna'>CZK</option>
<option value='DJF' title='Djiboutian Franc'>DJF</option>
<option value='DKK' title='Danish Krone'>DKK</option>
<option value='DOP' title='Dominican Peso'>DOP</option>
<option value='DZD' title='Algerian Dinar'>DZD</option>
<option value='EEK' title='Estonian Kroon'>EEK</option>
<option value='EGP' title='Egyptian Pound'>EGP</option>
<option value='ERN' title='Eritrean Nakfa'>ERN</option>
<option value='ETB' title='Ethiopian Birr'>ETB</option>
<option value='EUR' title='Euro'>EUR</option>
<option value='FJD' title='Fijian Dollar'>FJD</option>
<option value='FKP' title='Falkland Islands Pound'>FKP</option>
<option value='GBP' title='British Pound Sterling'>GBP</option>
<option value='GEL' title='Georgian Lari'>GEL</option>
<option value='GGP' title='Guernsey Pound'>GGP</option>
<option value='GHS' title='Ghanaian Cedi'>GHS</option>
<option value='GIP' title='Gibraltar Pound'>GIP</option>
<option value='GMD' title='Gambian Dalasi'>GMD</option>
<option value='GNF' title='Guinean Franc'>GNF</option>
<option value='GTQ' title='Guatemalan Quetzal'>GTQ</option>
<option value='GYD' title='Guyanaese Dollar'>GYD</option>
<option value='HKD' title='Hong Kong Dollar'>HKD</option>
<option value='HNL' title='Honduran Lempira'>HNL</option>
<option value='HRK' title='Croatian Kuna'>HRK</option>
<option value='HTG' title='Haitian Gourde'>HTG</option>
<option value='HUF' title='Hungarian Forint'>HUF</option>
<option value='IDR' title='Indonesian Rupiah'>IDR</option>
<option value='ILS' title='Israeli New Sheqel'>ILS</option>
<option value='IMP' title='Manx pound'>IMP</option>
<option value='INR' title='Indian Rupee'>INR</option>
<option value='IQD' title='Iraqi Dinar'>IQD</option>
<option value='IRR' title='Iranian Rial'>IRR</option>
<option value='ISK' title='Icelandic Króna'>ISK</option>
<option value='JEP' title='Jersey Pound'>JEP</option>
<option value='JMD' title='Jamaican Dollar'>JMD</option>
<option value='JOD' title='Jordanian Dinar'>JOD</option>
<option value='JPY' title='Japanese Yen'>JPY</option>
<option value='KES' title='Kenyan Shilling'>KES</option>
<option value='KGS' title='Kyrgystani Som'>KGS</option>
<option value='KHR' title='Cambodian Riel'>KHR</option>
<option value='KMF' title='Comorian Franc'>KMF</option>
<option value='KPW' title='North Korean Won'>KPW</option>
<option value='KRW' title='South Korean Won'>KRW</option>
<option value='KWD' title='Kuwaiti Dinar'>KWD</option>
<option value='KYD' title='Cayman Islands Dollar'>KYD</option>
<option value='KZT' title='Kazakhstani Tenge'>KZT</option>
<option value='LAK' title='Laotian Kip'>LAK</option>
<option value='LBP' title='Lebanese Pound'>LBP</option>
<option value='LKR' title='Sri Lankan Rupee'>LKR</option>
<option value='LRD' title='Liberian Dollar'>LRD</option>
<option value='LSL' title='Lesotho Loti'>LSL</option>
<option value='LTL' title='Lithuanian Litas'>LTL</option>
<option value='LVL' title='Latvian Lats'>LVL</option>
<option value='LYD' title='Libyan Dinar'>LYD</option>
<option value='MAD' title='Moroccan Dirham'>MAD</option>
<option value='MDL' title='Moldovan Leu'>MDL</option>
<option value='MGA' title='Malagasy Ariary'>MGA</option>
<option value='MKD' title='Macedonian Denar'>MKD</option>
<option value='MMK' title='Myanma Kyat'>MMK</option>
<option value='MNT' title='Mongolian Tugrik'>MNT</option>
<option value='MOP' title='Macanese Pataca'>MOP</option>
<option value='MRO' title='Mauritanian Ouguiya'>MRO</option>
<option value='MUR' title='Mauritian Rupee'>MUR</option>
<option value='MVR' title='Maldivian Rufiyaa'>MVR</option>
<option value='MWK' title='Malawian Kwacha'>MWK</option>
<option value='MXN' title='Mexican Peso'>MXN</option>
<option value='MYR' title='Malaysian Ringgit'>MYR</option>
<option value='MZN' title='Mozambican Metical'>MZN</option>
<option value='NAD' title='Namibian Dollar'>NAD</option>
<option value='NGN' title='Nigerian Naira'>NGN</option>
<option value='NIO' title='Nicaraguan Córdoba'>NIO</option>
<option value='NOK' title='Norwegian Krone'>NOK</option>
<option value='NPR' title='Nepalese Rupee'>NPR</option>
<option value='NZD' title='New Zealand Dollar'>NZD</option>
<option value='OMR' title='Omani Rial'>OMR</option>
<option value='PAB' title='Panamanian Balboa'>PAB</option>
<option value='PEN' title='Peruvian Nuevo Sol'>PEN</option>
<option value='PGK' title='Papua New Guinean Kina'>PGK</option>
<option value='PHP' title='Philippine Peso'>PHP</option>
<option value='PKR' title='Pakistani Rupee'>PKR</option>
<option value='PLN' title='Polish Zloty'>PLN</option>
<option value='PYG' title='Paraguayan Guarani'>PYG</option>
<option value='QAR' title='Qatari Rial'>QAR</option>
<option value='RON' title='Romanian Leu'>RON</option>
<option value='RSD' title='Serbian Dinar'>RSD</option>
<option value='RUB' title='Russian Ruble'>RUB</option>
<option value='RWF' title='Rwandan Franc'>RWF</option>
<option value='SAR' title='Saudi Riyal'>SAR</option>
<option value='SBD' title='Solomon Islands Dollar'>SBD</option>
<option value='SCR' title='Seychellois Rupee'>SCR</option>
<option value='SDG' title='Sudanese Pound'>SDG</option>
<option value='SEK' title='Swedish Krona'>SEK</option>
<option value='SGD' title='Singapore Dollar'>SGD</option>
<option value='SHP' title='Saint Helena Pound'>SHP</option>
<option value='SLL' title='Sierra Leonean Leone'>SLL</option>
<option value='SOS' title='Somali Shilling'>SOS</option>
<option value='SRD' title='Surinamese Dollar'>SRD</option>
<option value='STD' title='São Tomé and Príncipe Dobra'>STD</option>
<option value='SVC' title='Salvadoran Colón'>SVC</option>
<option value='SYP' title='Syrian Pound'>SYP</option>
<option value='SZL' title='Swazi Lilangeni'>SZL</option>
<option value='THB' title='Thai Baht'>THB</option>
<option value='TJS' title='Tajikistani Somoni'>TJS</option>
<option value='TMT' title='Turkmenistani Manat'>TMT</option>
<option value='TND' title='Tunisian Dinar'>TND</option>
<option value='TOP' title='Tongan Pa?anga'>TOP</option>
<option value='TRY' title='Turkish Lira'>TRY</option>
<option value='TTD' title='Trinidad and Tobago Dollar'>TTD</option>
<option value='TWD' title='New Taiwan Dollar'>TWD</option>
<option value='TZS' title='Tanzanian Shilling'>TZS</option>
<option value='UAH' title='Ukrainian Hryvnia'>UAH</option>
<option value='UGX' title='Ugandan Shilling'>UGX</option>
<option value='USD' title='United States Dollar'>USD</option>
<option value='UYU' title='Uruguayan Peso'>UYU</option>
<option value='UZS' title='Uzbekistan Som'>UZS</option>
<option value='VEF' title='Venezuelan Bolívar'>VEF</option>
<option value='VND' title='Vietnamese Dong'>VND</option>
<option value='VUV' title='Vanuatu Vatu'>VUV</option>
<option value='WST' title='Samoan Tala'>WST</option>
<option value='XAF' title='CFA Franc BEAC'>XAF</option>
<option value='XAG' title='Silver (troy ounce)'>XAG</option>
<option value='XAU' title='Gold (troy ounce)'>XAU</option>
<option value='XCD' title='East Caribbean Dollar'>XCD</option>
<option value='XDR' title='Special Drawing Rights'>XDR</option>
<option value='XOF' title='CFA Franc BCEAO'>XOF</option>
<option value='XPF' title='CFP Franc'>XPF</option>
<option value='YER' title='Yemeni Rial'>YER</option>
<option value='ZAR' title='South African Rand'>ZAR</option>
<option value='ZMK' title='Zambian Kwacha (pre-2013)'>ZMK</option>
<option value='ZMW' title='Zambian Kwacha'>ZWL</option>
<option value='ZWL' title='Zimbabwean Dollar'>ZWL</option>
"""
@app.route('/currency_exchange', methods=['GET', 'POST'])
def currency_exchange():
    conversion_result = None
    message = None

    if request.method == 'POST':
        try:
            base_currency = request.form['base_currency']
            target_currency = request.form['target_currency']
            amount = float(request.form['amount'])

            if amount <= 0:
                raise ValueError("Amount must be a positive number.")
            if amount > 1_000_000_000_000:
                raise ValueError("Amount is too large. Maximum allowed is 1,000,000,000,000.")

            converted_amount = money.convert_currency(amount, base_currency, target_currency)

            converted_amount = round(converted_amount, 3)

            message = f"{amount} {base_currency} to {target_currency} is {converted_amount}"
        except ValueError as e:
            message = f"Error: {str(e)}"
        except (TypeError, Exception):
            message = "Invalid input or conversion error."

    return render_template('currency_exchange.html', result=message, dropdown_options=CURRENCY_OPTIONS)
'''


if __name__ == '__main__':
    setup_database()
    app.run(debug=True)
