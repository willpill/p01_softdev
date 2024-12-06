from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
import os
from werkzeug.security import generate_password_hash, check_password_hash
from build_db import setup_database
import keys 
app = Flask(__name__)
app.secret_key = os.urandom(24)
currency_key = keys.get_key("keys_currencylayer.txt")
fixer_key = keys.get_key("keys_fixer.txt")
marketstack_key = keys.get_key("keys_marketstack.txt")
modelingprep_key =  keys.get_key("keys_financialmodelingprep.txt")
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
        password = request.form['password']
        email = request.form['email']
        password_hash = generate_password_hash(password)

        conn = get_db_connection()
        try:
            conn.execute(
                'INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)',
                (username, email, password_hash))
            conn.commit()
        except sqlite3.IntegrityError:
            flash('Username or email already exists', 'danger')
            return redirect(url_for('register'))
        finally:
            conn.close()
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/currency_exchange')
def currency_exchange():
    return render_template('currency_exchange.html')

@app.route('/market_data')
def market_data():
    return render_template('market_data.html')

if __name__ == '__main__':
    app.run(debug=True)
