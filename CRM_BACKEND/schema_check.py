from Database import db_query
columns = db_query("SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'orders'")
for col in columns:
    print(col)
