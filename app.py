# app.py
from flask import Flask, request, redirect, render_template, url_for, flash
import sqlite3, string, random

app = Flask(__name__)
app.secret_key = 'your_secret_key'

DATABASE = 'urls.db'

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def generate_short_id():
    chars = string.ascii_letters + string.digits
    return ''.join(random.choices(chars, k=6))

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        long_url = request.form['long_url']
        if long_url:
            short_id = generate_short_id()

            # Insert into the database
            conn = get_db_connection()
            try:
                conn.execute('INSERT INTO urls (long_url, short_id) VALUES (?, ?)', (long_url, short_id))
                conn.commit()
                flash(f"Short URL created: {request.host_url}{short_id}")
            except sqlite3.IntegrityError:
                flash("Error: URL could not be shortened. Please try again.")
            finally:
                conn.close()
            return redirect(url_for('index'))
    return render_template('index.html')

@app.route('/<short_id>')
def redirect_url(short_id):
    conn = get_db_connection()
    url_entry = conn.execute('SELECT long_url FROM urls WHERE short_id = ?', (short_id,)).fetchone()
    conn.close()
    if url_entry:
        return redirect(url_entry['long_url'])
    else:
        flash("URL not found.")
        return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)