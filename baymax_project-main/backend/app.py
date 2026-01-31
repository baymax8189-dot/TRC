from flask import Flask, jsonify, request
from flask_cors import CORS
import psycopg2
from psycopg2.extras import RealDictCursor, execute_values
from datetime import datetime, timedelta
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

DATABASE_URL = os.getenv('DATABASE_URL')

def get_db_connection():
    return psycopg2.connect(DATABASE_URL)

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS stocks (
            id SERIAL PRIMARY KEY,
            run_timestamp TIMESTAMP NOT NULL,
            symbol VARCHAR(20) NOT NULL,
            stock_name VARCHAR(100),
            pct_chg DECIMAL(10,2),
            price DECIMAL(15,2),
            volume BIGINT,
            links VARCHAR(50),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        CREATE INDEX IF NOT EXISTS idx_symbol ON stocks(symbol);
        CREATE INDEX IF NOT EXISTS idx_timestamp ON stocks(run_timestamp);
        CREATE INDEX IF NOT EXISTS idx_created ON stocks(created_at);
    """)
    
    conn.commit()
    cursor.close()
    conn.close()
    logger.info("✓ Database initialized")

# ==================== ANALYTICS LAYER (Logic) ====================

def get_market_overview():
    """Calculate real-time market metrics"""
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    # Get latest data point for each symbol
    cursor.execute("""
        SELECT DISTINCT ON (symbol) 
            symbol, stock_name, pct_chg, price, volume, created_at
        FROM stocks
        ORDER BY symbol, created_at DESC
    """)
    
    latest_stocks = cursor.fetchall()
    cursor.close()
    conn.close()
    
    if not latest_stocks:
        return None
    
    # Calculate analytics
    total_symbols = len(latest_stocks)
    market_avg = sum([s['pct_chg'] or 0 for s in latest_stocks]) / total_symbols if total_symbols > 0 else 0
    gainers_5pct = len([s for s in latest_stocks if (s['pct_chg'] or 0) > 5])
    losers_5pct = len([s for s in latest_stocks if (s['pct_chg'] or 0) < -5])
    total_volume = sum([s['volume'] or 0 for s in latest_stocks])
    
    return {
        'total_symbols': total_symbols,
        'market_avg': round(market_avg, 2),
        'gainers_5pct': gainers_5pct,
        'losers_5pct': losers_5pct,
        'total_volume': total_volume,
        'timestamp': datetime.now().isoformat()
    }

def get_top_performers():
    """Analyze and rank top gaining stocks"""
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    cursor.execute("""
        SELECT 
            symbol, stock_name,
            ROUND(AVG(pct_chg)::numeric, 2) as avg_gain,
            MAX(pct_chg) as max_gain,
            MIN(pct_chg) as min_gain,
            MAX(price) as max_price,
            MAX(volume) as max_volume,
            COUNT(*) as occurrences,
            MAX(created_at) as last_updated
        FROM stocks
        WHERE created_at > NOW() - INTERVAL '1 hour'
        GROUP BY symbol, stock_name
        HAVING COUNT(*) >= 3
        ORDER BY avg_gain DESC 
        LIMIT 25
    """)
    
    results = cursor.fetchall()
    cursor.close()
    conn.close()
    
    return results

def get_momentum_stocks():
    """Identify stocks with strong upward momentum"""
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    cursor.execute("""
        SELECT 
            symbol, stock_name,
            ROUND(AVG(pct_chg)::numeric, 2) as avg_gain,
            COUNT(*) as appearances,
            MAX(created_at) as last_updated,
            ROUND((MAX(pct_chg) - MIN(pct_chg))::numeric, 2) as volatility
        FROM stocks
        WHERE created_at > NOW() - INTERVAL '30 minutes'
        GROUP BY symbol, stock_name
        HAVING COUNT(*) >= 25 AND AVG(pct_chg) > 0
        ORDER BY avg_gain DESC, appearances DESC
        LIMIT 20
    """)
    
    results = cursor.fetchall()
    cursor.close()
    conn.close()
    
    return results

def get_breakout_analysis():
    """Find stocks breaking out from consolidation"""
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    cursor.execute("""
        SELECT 
            symbol, stock_name,
            ROUND(MAX(price)::numeric, 2) as price_high,
            ROUND(MIN(price)::numeric, 2) as price_low,
            ROUND(MAX(pct_chg)::numeric, 2) as max_gain,
            ROUND((MAX(price) - MIN(price))::numeric, 2) as price_range,
            ROUND(AVG(volume)::numeric, 0) as avg_volume,
            MAX(created_at) as last_updated
        FROM stocks
        WHERE created_at > NOW() - INTERVAL '15 minutes'
        GROUP BY symbol, stock_name
        HAVING (MAX(price) - MIN(price)) > (AVG(price) * 0.02)
        ORDER BY max_gain DESC
        LIMIT 20
    """)
    
    results = cursor.fetchall()
    cursor.close()
    conn.close()
    
    return results

# ==================== API ENDPOINTS ====================

@app.route('/api/data/insert', methods=['POST'])
def insert_data():
    """Bulk insert for 1-min interval"""
    data = request.json
    if not data:
        return jsonify({"error": "No data"}), 400
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        run_time = datetime.now()
        
        values = [
            (
                run_time,
                row.get('Symbol', ''),
                row.get('Stock Narr', ''),
                float(row.get('%Chg', 0)) if row.get('%Chg') else 0,
                float(row.get('Price', 0)) if row.get('Price') else 0,
                int(row.get('Volume', 0)) if row.get('Volume') else 0,
                row.get('Links', '')
            )
            for row in data
        ]
        
        execute_values(
            cursor,
            """
            INSERT INTO stocks (run_timestamp, symbol, stock_name, pct_chg, price, volume, links)
            VALUES %s
            """,
            values
        )
        
        conn.commit()
        cursor.close()
        conn.close()
        
        logger.info(f"✓ Inserted {len(data)} records")
        return jsonify({"status": "success", "rows": len(data), "timestamp": run_time.isoformat()})
    
    except Exception as e:
        conn.rollback()
        cursor.close()
        conn.close()
        logger.error(f"Insert error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/dashboard/latest', methods=['GET'])
def latest_data():
    """Get latest stock data"""
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    cursor.execute("""
        SELECT DISTINCT ON (symbol)
            * FROM stocks 
        ORDER BY symbol, created_at DESC
        LIMIT 100
    """)
    
    stocks = cursor.fetchall()
    cursor.close()
    conn.close()
    
    return jsonify(stocks)

@app.route('/api/dashboard/stats', methods=['GET'])
def dashboard_stats():
    """Get market overview using analytics layer"""
    try:
        stats = get_market_overview()
        return jsonify(stats) if stats else jsonify({}), 200
    except Exception as e:
        logger.error(f"Stats error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/analytics/top-gainers', methods=['GET'])
def top_gainers():
    """Get top gaining stocks using analytics layer"""
    try:
        results = get_top_performers()
        return jsonify(results)
    except Exception as e:
        logger.error(f"Top gainers error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/analytics/momentum', methods=['GET'])
def momentum_stocks():
    """Get momentum stocks (strong upward trend)"""
    try:
        results = get_momentum_stocks()
        return jsonify(results)
    except Exception as e:
        logger.error(f"Momentum error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/analytics/breakouts', methods=['GET'])
def breakout_stocks():
    """Get breakout stocks (price volatility)"""
    try:
        results = get_breakout_analysis()
        return jsonify(results)
    except Exception as e:
        logger.error(f"Breakout error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/analytics/top-gainers-old', methods=['GET'])
def top_gainers_old():
    """Legacy endpoint"""
    try:
        results = get_top_performers()
        return jsonify(results)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    try:
        conn = get_db_connection()
        conn.close()
        return jsonify({"status": "healthy", "timestamp": datetime.now().isoformat()})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    init_db()
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
