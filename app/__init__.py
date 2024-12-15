import os
import sqlite3
import keys

import money
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash

from build_db import setup_database

app = Flask(__name__)
app.secret_key = os.urandom(24)
currency_key = "a6bc55e4910ba85a6b590df72c94b1b7"#keys.get_key("keys_currencylayer.txt")
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
        return render_template('home.html', user=user_data)
    return render_template('home.html', user=None)

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        conn.close()

        if user and check_password_hash(user['password_hash'], password):
            session['username'] = username
            flash('Login successful!', 'success')
            return redirect(url_for('home'))
        flash('Invalid username or password', 'danger')
    return render_template('login.html')

@app.route('/logout', methods=['GET','POST'])
def logout():
    session.pop('username', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('home'))

@app.route('/register', methods=['GET','POST'])
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
                (username, email, password_hash))
            conn.commit()
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Username or email already exists', 'danger')
        finally:
            conn.close()
    return render_template('register.html')
CURRENCY_OPTIONS = """
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
<option value='BZD' title='Belize Dollar'>BZD</option>
<option value='CAD' title='Canadian Dollar'>CAD</option>
<option value='CHF' title='Swiss Franc'>CHF</option>
<option value='CNY' title='Chinese Yuan'>CNY</option>
<option value='COP' title='Colombian Peso'>COP</option>
<option value='CRC' title='Costa Rican Colón'>CRC</option>
<option value='CUP' title='Cuban Peso'>CUP</option>
<option value='CZK' title='Czech Republic Koruna'>CZK</option>
<option value='DKK' title='Danish Krone'>DKK</option>
<option value='DOP' title='Dominican Peso'>DOP</option>
<option value='EGP' title='Egyptian Pound'>EGP</option>
<option value='EUR' title='Euro'>EUR</option>
<option value='GBP' title='British Pound Sterling'>GBP</option>
<option value='HKD' title='Hong Kong Dollar'>HKD</option>
<option value='INR' title='Indian Rupee'>INR</option>
<option value='JPY' title='Japanese Yen'>JPY</option>
<option value='KES' title='Kenyan Shilling'>KES</option>
<option value='KRW' title='South Korean Won'>KRW</option>
<option value='MXN' title='Mexican Peso'>MXN</option>
<option value='NGN' title='Nigerian Naira'>NGN</option>
<option value='NOK' title='Norwegian Krone'>NOK</option>
<option value='NZD' title='New Zealand Dollar'>NZD</option>
<option value='USD' title='United States Dollar'>USD</option>
<option value='ZAR' title='South African Rand'>ZAR</option>
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



if __name__ == '__main__':
    setup_database()
    app.run(debug=True)
