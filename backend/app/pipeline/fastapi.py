from enum import Enum
from fastapi import FastAPI
from pydantic import BaseModel
import psycopg2


app = FastAPI()


class Category(Enum):
    TOOLS = "tools"
    CONSUMABLES = "consumables"


class Item(BaseModel):
    name: str
    price: float
    count: int
    id: int
    category: Category


items = {
    0: Item(name="Hammer", price=9.99, count=20, id=0, category=Category.TOOLS),
    1: Item(name="Pliers", price=5.99, count=20, id=1, category=Category.TOOLS),
    2: Item(name="Nails", price=1.99, count=100, id=2, category=Category.CONSUMABLES),
}


# FastAPI handles JSON serialization and deserialization for us.
# We can simply use built-in python and Pydantic types, in this case dict[int, Item].
@app.get("/")
def index() -> dict[str, dict[int, Item]]:
    return {"items": items}


###


app = FastAPI()


def get_connection():
    return psycopg2.connect(
        "postgresql://neondb_owner:npg_0Qymwkv1RfrJ@ep-dark-field-a4q9jhv8-pooler.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"
    )


@app.get("/")
def read_from_neon():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT * FROM playing_with_neon;")
    rows = cur.fetchall()

    # Get column names dynamically
    colnames = [desc[0] for desc in cur.description]

    cur.close()
    conn.close()

    # Convert rows to list of dicts
    output = [dict(zip(colnames, row)) for row in rows]

    return {"data": output}
