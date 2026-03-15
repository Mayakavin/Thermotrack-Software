import sqlite3
import os
from flask import Flask, request, jsonify, render_template
from datetime import datetime, timedelta

app = Flask(__name__)

# Use an absolute path to avoid "Database not found" errors on PythonAnywhere
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(BASE_DIR, "fridge_data.db")
def init_db():
    with sqlite3.connect(DB_FILE) as conn:
        # Added power and health to the initial creation
        conn.execute('''CREATE TABLE IF NOT EXISTS logs
                        (id INTEGER PRIMARY KEY AUTOINCREMENT,
                         timestamp DATETIME,
                         temp REAL,
                         current REAL,
                         status TEXT,
                         power REAL,
                         health INTEGER)''')
init_db()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/update', methods=['POST'])
@app.route('/update', methods=['POST'])
def update():
    try:
        data = request.json
        if not data:
            return jsonify({"status": "error", "message": "No data received"}), 400

        temp = float(data.get('temp', 0))
        current = float(data.get('current', 0))
        status = data.get('status', 'Healthy')

        ist_time = (datetime.utcnow() + timedelta(hours=5, minutes=30)).strftime('%Y-%m-%d %H:%M:%S')

        with sqlite3.connect(DB_FILE) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            # --- STEP 1: GET PREVIOUS DATA FIRST ---
            cursor.execute("SELECT power, health FROM logs ORDER BY id DESC LIMIT 1")
            last_row = cursor.fetchone()

            # --- STEP 2: POWER CALCULATION ---
            new_increment = (220 * current * 3.6) / 1000.0
            total_power = (last_row['power'] + new_increment) if last_row else new_increment

            # --- STEP 3: HEALTH CALCULATION (Using last_row safely) ---
            prev_h = last_row['health'] if (last_row and last_row['health'] is not None) else 100

            if "TRIP" in status or "CRITICAL" in status:
                new_h = prev_h - 5
            elif "HEALING" in status:
                new_h = prev_h
            else:
                new_h = prev_h + 0.5

            health = max(0, min(100, new_h))

            # --- STEP 4: SAVE ---
            conn.execute("INSERT INTO logs (timestamp, temp, current, status, power, health) VALUES (?, ?, ?, ?, ?, ?)",
                         (ist_time, temp, current, status, total_power, health))
            conn.commit()

        return jsonify({"status": "success"})
    except Exception as e:
        print(f"Update Error: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500
@app.route('/get_data')
def get_data():
    try:
        with sqlite3.connect(DB_FILE) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("SELECT * FROM logs ORDER BY id DESC LIMIT 50")
            rows = cursor.fetchall()
            return jsonify([dict(row) for row in rows][::-1])
    except Exception as e:
        return jsonify([])

@app.route('/clear_data', methods=['POST'])
def clear_data():
    try:
        with sqlite3.connect(DB_FILE) as conn:
            conn.execute("DELETE FROM logs")
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})
