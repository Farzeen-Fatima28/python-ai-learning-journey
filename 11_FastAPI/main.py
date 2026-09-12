from fastapi import FastAPI
import sqlite3
from pydantic import BaseModel

app = FastAPI()


class Product(BaseModel):
    id: int
    name: str
    price: int

    
# Basic route (/) — no parameters
@app.get("/")
def read_root():
    return {"message": "Hello World"}

# Path parameter — value comes from the URL itself, auto-validated as int
@app.get("/items/{item_id}")
def read_item(item_id : int):
    return {"item_id": item_id}

# Query parameters — ?q=...&limit=... style, limit has a default
@app.get("/search")
def read_search(q: str, limit: int = 10):
    return {"query": q, "limit": limit}

@app.get("/margin")
def read_margin(revenue: float, expenses: float):
    profit = revenue - expenses
    margin_percent = (profit / revenue)*100
    return {
        "profit": profit, "margin_percent": margin_percent
}


# Pydantic model — defines the shape of data this API accepts
from pydantic import BaseModel

class Expense(BaseModel):
    amount: float
    category: str
    date: str

# POST route — accepts a full JSON body, validated against Expense
@app.post("/expenses")
def create_expense(expense: Expense):
    return {"received": expense}



from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()
client = genai.Client()

class Review(BaseModel):
    text: str

class Sentiment(BaseModel):
    label: str
    score: int

@app.post("/sentiment")
def analyze_sentiment(review: Review):
    response = client.models.generate_content(
        model="gemini-3.5-flash",
        contents=(
            "Find the sentiment of this customer review. "
            "label must be 'positive', 'negative', or 'neutral'. "
            "score must be a number from 1 (very bad) to 5 (very good). "
            f"Review: {review.text}"
        ),
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=Sentiment,
        ),
    )
    return response.parsed



@app.get("/products")
def get_products():
    conn = sqlite3.connect("../12_databases/products.db")
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, name, price FROM products")
    rows = cursor.fetchall()
    
    conn.close()
    
    products = [Product(id=row[0], name=row[1], price=row[2]) for row in rows]
    return products
