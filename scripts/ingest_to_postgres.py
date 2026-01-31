import os
import pandas as pd
import psycopg2
from psycopg2.extras import execute_values
from datetime import datetime

# CONFIGURATION
CSV_DIR = os.environ.get('CSV_DIR', r'C:/Users/saikumar/Desktop/chartlink/15_minute')
DB_HOST = os.environ.get('PGHOST', 'localhost')
DB_PORT = os.environ.get('PGPORT', '5432')
DB_NAME = os.environ.get('PGDATABASE', 'stocks')
DB_USER = os.environ.get('PGUSER', 'postgres')
DB_PASS = os.environ.get('PGPASSWORD', 'password')

# Connect to PostgreSQL
def get_connection():
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASS
    )

def process_csv_files():
    today_date = datetime.now().date()
    files = [f for f in os.listdir(CSV_DIR) if os.path.isfile(os.path.join(CSV_DIR, f))]
    files.sort(key=lambda x: os.path.getctime(os.path.join(CSV_DIR, x)), reverse=True)
    all_dfs = []
    for file in files:
        if file.startswith(f"15_minutes_{today_date.strftime('%Y%m%d')}"):
            file_path = os.path.join(CSV_DIR, file)
            try:
                df = pd.read_csv(file_path).drop(['Sr.','Links'], axis=1)
            except Exception as e:
                print(f"Skipping {file}: {e}")
                continue
            column_name_mapping = {'Stock Name': 'stock', 'Symbol': 'symbol', '%Chg': 'chg_percentage','Price':'price','Volume':'volume'}
            df.rename(columns=column_name_mapping, inplace=True)
            df['chg_percentage'] = pd.to_numeric(df['chg_percentage'].astype(str).str.rstrip('%'), errors='coerce')
            try:
                file_date = pd.to_datetime(file.split('_')[2], format='%Y%m%d').date()
                number = file.split('_')[3].split('.')[0]
            except (ValueError, IndexError):
                print(f"Skipping file '{file}' due to unexpected filename format.")
                continue
            df['file_date'] = file_date
            df['number'] = number
            all_dfs.append(df)
    if not all_dfs:
        print("No files found for today.")
        return pd.DataFrame()
    df_15min = pd.concat(all_dfs, ignore_index=True)
    df_15min['number'] = pd.to_datetime(df_15min['number'], format='%H%M%S').dt.strftime('%H:%M:%S')
    df_15min['timestamp'] = pd.to_datetime(df_15min['file_date'].astype(str) + ' ' + df_15min['number'])
    df_15min = df_15min.drop(['file_date','number'], axis=1)
    df_15min['timestamp'] = pd.to_datetime(df_15min['timestamp'])
    df_15min['date_'] = df_15min['timestamp'].dt.date
    return df_15min

def save_to_postgres(df):
    if df.empty:
        print("No data to insert.")
        return
    conn = get_connection()
    cur = conn.cursor()
    insert_query = '''
        INSERT INTO stock_ticks (symbol, stock, price, chg_percentage, volume, timestamp, created_at)
        VALUES %s
        ON CONFLICT DO NOTHING
    '''
    values = [
        (
            row['symbol'],
            row['stock'],
            float(row['price']) if not pd.isnull(row['price']) else None,
            float(row['chg_percentage']) if not pd.isnull(row['chg_percentage']) else None,
            int(row['volume']) if not pd.isnull(row['volume']) else None,
            row['timestamp'],
            datetime.now()
        )
        for _, row in df.iterrows()
    ]
    try:
        execute_values(cur, insert_query, values)
        conn.commit()
        print(f"Inserted {len(values)} rows into stock_ticks.")
    except Exception as e:
        print(f"Error inserting to DB: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()

def main():
    df = process_csv_files()
    save_to_postgres(df)

if __name__ == "__main__":
    main()
