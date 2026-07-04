import os
import psycopg
from dotenv import load_dotenv

load_dotenv()
db_url = os.getenv("DATABASE_URL")
print("Connecting to:", db_url)

with psycopg.connect(db_url) as conn:
    with conn.cursor() as cur:
        # Get all tables
        cur.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public';
        """)
        tables = cur.fetchall()
        print("Tables:")
        for t in tables:
            tname = t[0]
            print(f"\nTable: {tname}")
            # Get columns
            cur.execute(f"""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns
                WHERE table_name = '{tname}';
            """)
            cols = cur.fetchall()
            for col in cols:
                print(f"  - {col[0]}: {col[1]} (Nullable: {col[2]})")
