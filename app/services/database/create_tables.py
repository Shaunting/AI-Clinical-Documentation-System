import psycopg2

conn = psycopg2.connect(
    "postgresql://neondb_owner:npg_0Qymwkv1RfrJ@ep-dark-field-a4q9jhv8-pooler.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"
)

cur = conn.cursor()

with open("schema.sql", "r") as f:
    sql_script = f.read()

cur.execute(sql_script)

conn.commit()
cur.close()
conn.close()

print("Database schema applied.")
