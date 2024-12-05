from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
import os
from werkzeug.security import generate_password_hash, check_password_hash
from build_db import setup_database

app = Flask(__name__)
app.secret_key = os.urandom(24)

def get_db_connection():
    conn = sqlite3.connect('stonks.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def home():
    conn=get_db_connection()
    
@app.route('/login')
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
@app.route('/logout')
def logout():
    session.pop('username', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('home'))
@app.route('/register')
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        password_hash = generate_password_hash(password)

        conn = get_db_connection()
        try:
            conn.execute(
                'INSERT INTO users (username, password_hash) VALUES (?, ?)',
                (username, password_hash))
            conn.commit()
        except sqlite3.IntegrityError:
            return 'Username already exists'
        finally:
            conn.close()
        return redirect(url_for('login'))
    return render_template('register.html')
