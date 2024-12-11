import os
import sqlite3
import keys

from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash

from build_db import setup_database

app = Flask(__name__)
app.secret_key = os.urandom(24)
currency_key = "3640fcf307bd1020090b38674dbaeceb"#keys.get_key("keys_currencylayer.txt")
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

@app.route('/currency_exchange', methods=['GET', 'POST'])
def currency_exchange():
    conversion_result = None
    if request.method == 'POST':
        base_currency = request.form['base_currency']
        target_currency = request.form['target_currency']
        amount = float(request.form['amount'])
        response = requests.get(f"https://api.currencylayer.com/convert?access_key={currency_key}")
        data = response.json()
        if data['success']:
            rates = data['quotes']
            base_rate = rates.get(f"USD{base_currency.upper()}")
            target_rate = rates.get(f"USD{target_currency.upper()}")
            if base_rate and target_rate:
                conversion_result = round((amount / base_rate) * target_rate, 2)
            else: flash("Invalid currency code entered.", 'danger')
        else: flash("Error fetching exchange rates.", 'danger')
    return render_template('currency_exchange.html', result=conversion_result)

if __name__ == '__main__':
    setup_database()
    app.run(debug=True)
