import os
import dotenv
from Database import db_execute

dotenv.load_dotenv()

print("Starting DB migration...")

# 1. Alter reminders table to support categories
db_execute("ALTER TABLE reminders ADD COLUMN IF NOT EXISTS category VARCHAR(100) DEFAULT 'Other';")
print("Altered reminders table (added category column).")

# 2. Alter orders table to support source, priority, and followup_date
db_execute("ALTER TABLE orders ADD COLUMN IF NOT EXISTS source VARCHAR(100);")
db_execute("ALTER TABLE orders ADD COLUMN IF NOT EXISTS priority VARCHAR(100);")
db_execute("ALTER TABLE orders ADD COLUMN IF NOT EXISTS followup_date DATE;")
print("Altered orders table (added source, priority, followup_date columns).")

# 3. Create locked_inventory table
db_execute("""
CREATE TABLE IF NOT EXISTS locked_inventory (
    id SERIAL PRIMARY KEY,
    order_id INTEGER REFERENCES orders(id) ON DELETE CASCADE,
    customer_id INTEGER REFERENCES customers(id) ON DELETE CASCADE,
    inventory_id INTEGER REFERENCES inventory(id) ON DELETE CASCADE,
    quantity NUMERIC NOT NULL,
    locked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
""")
print("Created locked_inventory table.")

print("DB migration completed successfully!")
