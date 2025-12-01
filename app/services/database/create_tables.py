import os
import psycopg2
from dotenv import load_dotenv

# Load .env variables
load_dotenv()

# Read DATABASE_URL from environment
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is not set in the .env file")

# Connect to database
conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor()

# Read and execute schema.sql
with open("schema.sql", "r") as f:
    sql_script = f.read()

cur.execute(sql_script)

conn.commit()
cur.close()
conn.close()

print("Database schema applied.")
