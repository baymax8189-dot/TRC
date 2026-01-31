import os
from flask import Flask, jsonify, request
from flask_cors import CORS
import psycopg2
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Get database URL from environment variable (lazy load to avoid errors on startup)
def get_database_url():
    return os.environ.get("DATABASE_URL")

def get_db_connection():
    database_url = get_database_url()
    if not database_url:
        raise ValueError("DATABASE_URL environment variable is not set")
    conn = psycopg2.connect(database_url)
    return conn

@app.route("/")
def home():
    return jsonify({"message": "Chartlink Backend API is running!"})

@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status": "healthy", "timestamp": datetime.now().isoformat()})

@app.route("/api/stock-ticks", methods=["GET"])
def get_stock_ticks():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM stock_ticks LIMIT 100")
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return jsonify({"data": rows, "count": len(rows)})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/stock-ticks", methods=["POST"])
def add_stock_tick():
    try:
        data = request.json
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO stock_ticks (stock_name, symbol, links, percent_change, price, volume) VALUES (%s, %s, %s, %s, %s, %s)",
            (data.get("stock_name"), data.get("symbol"), data.get("links"), data.get("percent_change"), data.get("price"), data.get("volume"))
        )
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({"message": "Stock tick added successfully"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
