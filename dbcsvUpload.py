import psycopg2
import csv

# PostgreSQL credentials
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "markets"
DB_USER = "Kavish"
DB_PASSWORD = "97642654875"

CSV_FILE_PATH = "/Users/kavishambani/Downloads/ind_nifty200list(1).csv"

try:
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )
    cur = conn.cursor()
    print("✅ Connected to database.")
except Exception as conn_err:
    print("❌ Database connection failed:", conn_err)
    exit(1)

row_count = 0
try:
    with open(CSV_FILE_PATH, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        reader.fieldnames = [h.strip() for h in reader.fieldnames]

        required_fields = ["ISIN Code", "Company Name", "Industry", "Symbol", "Series"]
        field_map = {name: name for name in reader.fieldnames}

        for field in required_fields:
            if field not in field_map:
                raise Exception(f"Missing column in CSV: '{field}'")

        for row in reader:
            # Skip rows missing essential data
            if not all(row.get(field_map[key]) for key in ["ISIN Code", "Company Name", "Industry", "Symbol"]):
                continue

            cur.execute('''
                INSERT INTO "StockSymbol" (isin, symbol, "companyName", industry, series)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (isin) DO NOTHING
            ''', (
                row[field_map["ISIN Code"]].strip(),
                row[field_map["Symbol"]].strip(),
                row[field_map["Company Name"]].strip(),
                row[field_map["Industry"]].strip(),
                row[field_map["Series"]].strip() if row.get(field_map["Series"]) else ''
            ))
            row_count += 1

    conn.commit()
    print(f"✅ Successfully uploaded {row_count} rows to the database.")

except Exception as e:
    conn.rollback()
    print("❌ Error during data processing/upload:", e)

finally:
    cur.close()
    conn.close()
    print("🔒 Database connection closed.")
