import os
from dotenv import load_dotenv
import psycopg

load_dotenv()
db_url = os.getenv("DATABASE_URL")
print("Connecting to:", db_url)

with psycopg.connect(db_url) as conn:
    with conn.cursor() as cur:
        # Add note column to employee_locations table
        print("Altering employee_locations to add note column if not exists...")
        cur.execute("ALTER TABLE employee_locations ADD COLUMN IF NOT EXISTS note TEXT;")
        conn.commit()
        print("Table altered successfully!")
