import os
import psycopg
from app.services.db_service import get_conn

print("DATABASE_URL =", os.getenv("DATABASE_URL"))

conn = get_conn()

with conn.cursor() as cur:
    cur.execute("SELECT * FROM playing_with_neon;")
    now = cur.fetchone()
    print("Query SUCCESS:", now)

conn.close()
