import os
import psycopg
from dotenv import load_dotenv

load_dotenv()
db_url = os.getenv("DATABASE_URL")
print("Connecting to:", db_url)

commands = [
    # 1. Create roles table
    """
    CREATE TABLE IF NOT EXISTS roles (
        id SERIAL PRIMARY KEY,
        role_name VARCHAR(50) UNIQUE NOT NULL,
        created_by INTEGER,
        modified_by INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        modified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """,

    # 2. Seed initial roles
    """
    INSERT INTO roles (role_name) VALUES 
    ('ADMIN'), ('SALES'), ('INVENTORY'), ('PRODUCTION'), ('HR'), ('ACCOUNTANT')
    ON CONFLICT (role_name) DO NOTHING;
    """,

    # 3. Add role_id to users and populate it
    """
    ALTER TABLE users ADD COLUMN IF NOT EXISTS role_id INTEGER REFERENCES roles(id);
    """,
    """
    UPDATE users SET role_id = (SELECT id FROM roles WHERE roles.role_name = UPPER(users.role))
    WHERE role_id IS NULL;
    """,
    """
    UPDATE users SET role_id = (SELECT id FROM roles WHERE roles.role_name = 'SALES')
    WHERE role_id IS NULL;
    """,

    # 4. Make role_id NOT NULL and drop role string column
    # Wait, we can keep the column or drop it. Let's drop it to complete normalization.
    """
    ALTER TABLE users ALTER COLUMN role_id SET NOT NULL;
    """,
    """
    ALTER TABLE users DROP COLUMN IF EXISTS role;
    """,

    # 5. Create raw_materials master table
    """
    CREATE TABLE IF NOT EXISTS raw_materials (
        id SERIAL PRIMARY KEY,
        name VARCHAR(255) UNIQUE NOT NULL,
        unit VARCHAR(50),
        created_by INTEGER REFERENCES users(id) ON DELETE SET NULL,
        modified_by INTEGER REFERENCES users(id) ON DELETE SET NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        modified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """,

    # 6. Create products master table
    """
    CREATE TABLE IF NOT EXISTS products (
        id SERIAL PRIMARY KEY,
        name VARCHAR(255) UNIQUE NOT NULL,
        unit VARCHAR(50),
        created_by INTEGER REFERENCES users(id) ON DELETE SET NULL,
        modified_by INTEGER REFERENCES users(id) ON DELETE SET NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        modified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """,

    # 7. Add foreign keys to inventory table
    """
    ALTER TABLE inventory ADD COLUMN IF NOT EXISTS raw_material_id INTEGER REFERENCES raw_materials(id) ON DELETE CASCADE;
    """,
    """
    ALTER TABLE inventory ADD COLUMN IF NOT EXISTS product_id INTEGER REFERENCES products(id) ON DELETE CASCADE;
    """,

    # 8. Populate raw_materials and products from existing inventory table
    # We execute this programmatically in python to handle conflicts and mappings cleanly.
]

# Audit columns helper queries
audit_columns_tables = [
    ("users", ["created_by", "modified_by", "modified_at"]),
    ("attendance", ["created_by", "modified_by", "created_at", "modified_at"]),
    ("employee_locations", ["created_by", "modified_by", "created_at", "modified_at"]),
    ("customers", ["created_by", "modified_by", "modified_at"]),
    ("leads", ["modified_by", "modified_at"]), # We will rename created_by_id to created_by first
    ("orders", ["created_by", "modified_by", "modified_at"]),
    ("production", ["created_by", "modified_by", "created_at", "modified_at"]),
    ("invoices", ["created_by", "modified_by", "created_at", "modified_at"]),
    ("purchase_requests", ["created_by", "modified_by", "modified_at"]),
    ("indents", ["created_by", "modified_by", "modified_at"]),
    ("reminders", ["created_by", "modified_by", "modified_at"]),
    ("inventory", ["created_by", "modified_by", "created_at", "modified_at"])
]

with psycopg.connect(db_url) as conn:
    # Set autocommit to False to execute migrations in transaction
    conn.autocommit = False
    with conn.cursor() as cur:
        # Run baseline command sequences
        for cmd in commands:
            print("Running command:", cmd.strip().split('\n')[0])
            cur.execute(cmd)
        
        # Populate raw_materials and products tables from existing inventory before dropping columns
        cur.execute("SELECT id, item_name, category, unit FROM inventory")
        inv_items = cur.fetchall()
        for item_id, item_name, category, unit in inv_items:
            if category in ('Raw Material', 'Raw Materials'):
                # Insert into raw_materials
                cur.execute(
                    "INSERT INTO raw_materials (name, unit) VALUES (%s, %s) ON CONFLICT (name) DO UPDATE SET unit = EXCLUDED.unit RETURNING id",
                    (item_name, unit)
                )
                raw_mat_id = cur.fetchone()[0]
                cur.execute("UPDATE inventory SET raw_material_id = %s WHERE id = %s", (raw_mat_id, item_id))
            elif category in ('Indents', 'Finished Goods'):
                # Insert into products
                cur.execute(
                    "INSERT INTO products (name, unit) VALUES (%s, %s) ON CONFLICT (name) DO UPDATE SET unit = EXCLUDED.unit RETURNING id",
                    (item_name, unit)
                )
                prod_id = cur.fetchone()[0]
                cur.execute("UPDATE inventory SET product_id = %s WHERE id = %s", (prod_id, item_id))
        
        # Drop item_name and unit from inventory
        cur.execute("ALTER TABLE inventory DROP COLUMN IF EXISTS item_name")
        cur.execute("ALTER TABLE inventory DROP COLUMN IF EXISTS unit")

        # Handle leads created_by_id rename
        cur.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'leads' AND column_name = 'created_by_id';
        """)
        if cur.fetchone():
            print("Renaming leads.created_by_id to created_by")
            cur.execute("ALTER TABLE leads RENAME COLUMN created_by_id TO created_by;")

        # Set up self references on roles table for created_by and modified_by
        cur.execute("ALTER TABLE roles ADD CONSTRAINT fk_roles_created_by FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL;")
        cur.execute("ALTER TABLE roles ADD CONSTRAINT fk_roles_modified_by FOREIGN KEY (modified_by) REFERENCES users(id) ON DELETE SET NULL;")

        # Add audit columns to all tables
        for tname, cols in audit_columns_tables:
            for col in cols:
                if col in ("created_by", "modified_by"):
                    cur.execute(f"""
                        ALTER TABLE {tname} ADD COLUMN IF NOT EXISTS {col} INTEGER REFERENCES users(id) ON DELETE SET NULL;
                    """)
                elif col in ("created_at", "modified_at"):
                    cur.execute(f"""
                        ALTER TABLE {tname} ADD COLUMN IF NOT EXISTS {col} TIMESTAMP DEFAULT CURRENT_TIMESTAMP;
                    """)
        
        conn.commit()
        print("Database migration completed successfully!")
