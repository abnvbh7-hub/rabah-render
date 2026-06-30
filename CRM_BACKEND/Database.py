import os
import psycopg
from psycopg_pool import ConnectionPool
import dotenv
dotenv.load_dotenv()

def configure_conn(conn):
    conn.execute("SET TIME ZONE 'Asia/Kolkata';")
    conn.commit()

pool = ConnectionPool(
    conninfo=os.getenv("DATABASE_URL"),
    min_size=0,
    max_size=5,
    timeout=30.0,
    max_idle=30,
    configure=configure_conn
)

def db_query(query: str, params: tuple = None, fetch_one: bool = False):
    """Execute a query and return results as dictionary or list of dictionaries."""
    with pool.connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, params or ())
            if fetch_one:
                row = cur.fetchone()
                if row:
                    colnames = [desc[0] for desc in cur.description]
                    return dict(zip(colnames, row))
                return None
            else:
                try:
                    rows = cur.fetchall()
                    colnames = [desc[0] for desc in cur.description]
                    return [dict(zip(colnames, row)) for row in rows]
                except psycopg.ProgrammingError:

                    return []

def db_execute(query: str, params: tuple = None, return_id: bool = False):
    """Execute insert, update, delete operations. Optionally returns the returning ID if specified."""
    with pool.connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, params or ())
            val = None
            if return_id:
                row = cur.fetchone()
                if row:
                    val = row[0]
            conn.commit()
            return val
