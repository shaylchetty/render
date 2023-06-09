from flask import Flask, render_template, request, jsonify
import random
import json
import sqlite3

app = Flask(__name__)

# Set up the SQLite database connection
def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

# Create the database and players table if they don't exist
def create_database():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS players (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            score INTEGER
        )
    ''')
    conn.commit()
    conn.close()

# Decorator function to enable CORS
def enable_cors(func):
    def decorator(*args, **kwargs):
        response = func(*args, **kwargs)
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        response.headers.add('Access-Control-Allow-Methods', 'GET, POST')
        return response
    # Rename the decorator function
    decorator.__name__ = f"cors_enabled_{func.__name__}"
    return decorator

@app.route('/')
def home():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM players ORDER BY score DESC')
    players = cursor.fetchall()
    conn.close()
    return render_template('index.html', players=players)


@app.route('/update_score', methods=['POST'])
@enable_cors
def update_score():
    if request.method == 'POST':
        username = request.form.get('username')
        score = int(request.form.get('score'))

        conn = get_db_connection()
        cursor = conn.cursor()

        # Check if the player already exists in the database
        cursor.execute('SELECT * FROM players WHERE username = ?', (username,))
        player = cursor.fetchone()

        if player is None:
            # Player does not exist, insert a new record
            cursor.execute(
                'INSERT INTO players (username, score) VALUES (?, ?)', (username, score))
        else:
            # Player already exists, update the score
            cursor.execute(
                'UPDATE players SET score = ? WHERE username = ?', (score, username))

        conn.commit()
        conn.close()

        return 'Score updated successfully'


@app.route('/equatefunc')
@enable_cors
def equatefunc():
    a = random.randint(2, 100)  # Three random integers
    b = random.randint(2, 100)
    d = random.randint(2, 12)
    # choose randomly between addition, subtraction, multiplication, and division
    asmd = random.choice([1, 2, 3, 4])
    if asmd == 1:
        solve = a + b
        question = "%d + %d = " % (a, b)
    elif asmd == 2:
        if a > b:
            solve = a - b
            question = "%d - %d = " % (a, b)
        else:
            solve = b - a
            question = "%d - %d = " % (b, a)
    elif asmd == 3:
        solve = a * d
        question = "%d * %d = " % (a, d)
    else:
        solve = a
        c = a * d
        question = "%d / %d = " % (c, d)

    tup = [question, solve]

    return jsonify(tup)


if __name__ == '__main__':
    create_database()
    app.run(debug=True)
