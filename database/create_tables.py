import os
from pathlib import Path

import psycopg2
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

database_url = os.getenv("DATABASE_URL")
if not database_url:
    raise SystemExit("DATABASE_URL is not set. Copy .env.example to .env and add your Neon URL.")

conn = psycopg2.connect(database_url)

cur = conn.cursor()

with open("schema.sql", "r") as f:
    sql_script = f.read()

cur.execute(sql_script)

conn.commit()
cur.close()
conn.close()

print("Database schema applied.")
