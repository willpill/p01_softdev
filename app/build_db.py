import sqlite3

def setup_database():

    conn = sqlite3.connect('stonks.db')
    cursor = conn.cursor()

   
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY UNIQUE,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            current_balance FLOAT DEFAULT 0.0,
            stocks_owned TEXT NOT NULL
        )
    ''')


    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_stocks (
            username TEXT NOT NULL,
            ticker_symbol TEXT NOT NULL,
            quantity INT NOT NULL,
            PRIMARY KEY (username, ticker_symbol),
            FOREIGN KEY (username) REFERENCES users (username)
        )
    ''')


    cursor.execute('''
        CREATE TABLE IF NOT EXISTS stocks (
            stock_name TEXT NOT NULL,
            ticker_symbol TEXT PRIMARY KEY UNIQUE NOT NULL,
            price FLOAT NOT NULL,
            stock_sector TEXT,
            last_updated DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS rates (
            stock_name TEXT NOT NULL,
            ticker_symbol TEXT PRIMARY KEY UNIQUE NOT NULL,
            price FLOAT NOT NULL,
            stock_sector TEXT,
            last_updated DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()
    print("Database setup complete.")

if __name__ == '__main__':
    setup_database()
