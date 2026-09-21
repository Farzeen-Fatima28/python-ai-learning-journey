import os
import sqlite3
import time
from collections import Counter

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from google import genai
from google.genai import types
from pydantic import BaseModel, Field

# 1. Load API Key from local .env file
load_dotenv()

# 2. Initialize FastAPI App
app = FastAPI(title="Customer Feedback Analyzer API")

# Allow a frontend (Streamlit, React, etc.) running on a different port to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # fine for local dev; restrict this once deployed
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_FILE = "feedback.db"

# Google's model standard
MODEL_NAME = "gemini-3.6-flash"


# 3. Define Pydantic Models for Structured Output
class Review(BaseModel):
    review: str = Field(description="The original text of the review")
    label: str = Field(
        description="Sentiment label: positive, negative, or neutral"
    )
    score: int = Field(
        description="Sentiment score/rating from 1 (worst) to 5 (best)"
    )
    theme: str = Field(
        description="Primary topic discussed, e.g., delivery, quality, price, service"
    )


class Analysis(BaseModel):
    analyses: list[Review]


# 4. Pydantic Models for the API's own request/response bodies
class AnalyzeRequest(BaseModel):
    reviews_text: str = Field(
        description="Raw textarea content — one review per line"
    )


class AnalyzeResponse(BaseModel):
    results: list[Review]
    summary: dict


class SaveRequest(BaseModel):
    results: list[Review]


class SaveResponse(BaseModel):
    saved_count: int
    duplicates_skipped: int
    message: str


# 5. LLM Analysis Function
def analyze_reviews_with_gemini(
    reviews_list: list[str],
    max_retries: int = 3,
) -> list[Review]:
    """Sends a list of review strings to Gemini and receives structured output.

    Retries with a short backoff if the model is temporarily overloaded (503).
    """
    client = genai.Client()

    formatted_input = "\n".join(
        [f"- {rev}" for rev in reviews_list if rev.strip()]
    )
    prompt = f"Analyze the following customer reviews:\n{formatted_input}"

    last_error = None
    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=Analysis,
                    temperature=0.1,
                ),
            )
            result: Analysis = response.parsed
            return result.analyses

        except Exception as e:
            last_error = e
            # Only retry on "temporarily overloaded" style errors
            if "UNAVAILABLE" in str(e) or "503" in str(e):
                wait_time = 2**attempt  # 1s, 2s, 4s
                print(
                    f"Model overloaded, retrying in {wait_time}s... (attempt {attempt + 1}/{max_retries})"
                )
                time.sleep(wait_time)
                continue
            raise  # Any other error (bad request, auth, etc.) should fail immediately

    # Ran out of retries — surface the last error
    raise last_error


# 6. Summary Calculation Function
def calculate_summary_metrics(analyses: list[Review]) -> dict:
    """Calculates summary statistics from a list of Review objects."""
    if not analyses:
        return {
            "total_reviews": 0,
            "average_score": 0.0,
            "pct_positive": 0.0,
            "top_theme": "None",
        }

    total_reviews = len(analyses)
    total_score = sum(item.score for item in analyses)
    average_score = round(total_score / total_reviews, 1)

    positive_count = sum(
        1 for item in analyses if item.label.lower() == "positive"
    )
    pct_positive = round((positive_count / total_reviews) * 100)

    themes = [item.theme.lower() for item in analyses]
    most_common_theme = Counter(themes).most_common(1)[0][0] if themes else "N/A"

    return {
        "total_reviews": total_reviews,
        "average_score": average_score,
        "pct_positive": pct_positive,
        "top_theme": most_common_theme,
    }


# 7. Database Functions
def init_db():
    """Create the reviews table if it doesn't exist yet."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            review TEXT,
            label TEXT,
            score INTEGER,
            theme TEXT
        )
    """)
    conn.commit()
    conn.close()


def save_reviews_to_db(analyses: list[Review]) -> tuple[int, int]:
    """Saves reviews to database, skipping any review whose exact text is already saved.

    Returns (saved_count, duplicates_skipped).
    """
    init_db()
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # Retrieve all existing review texts
    cursor.execute("SELECT review FROM reviews")
    existing_reviews = {row[0] for row in cursor.fetchall()}

    # Filter out reviews already present in database
    new_items = [item for item in analyses if item.review not in existing_reviews]
    duplicates_skipped = len(analyses) - len(new_items)

    for item in new_items:
        cursor.execute(
            "INSERT INTO reviews (review, label, score, theme) VALUES (?, ?, ?, ?)",
            (item.review, item.label, item.score, item.theme),
        )

    conn.commit()
    conn.close()
    return len(new_items), duplicates_skipped


def load_all_reviews_from_db() -> list[dict]:
    """Read every saved review back from the database, most recent first."""
    init_db()
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT review, label, score, theme FROM reviews ORDER BY id DESC"
    )
    rows = cursor.fetchall()
    conn.close()

    return [
        {"review": r[0], "label": r[1], "score": r[2], "theme": r[3]}
        for r in rows
    ]


# 8. API Endpoints


@app.get("/")
def root():
    """Simple health check so you can confirm the server is running."""
    return {
        "status": "ok",
        "message": "Customer Feedback Analyzer API is running",
    }


@app.post("/analyze", response_model=AnalyzeResponse)
def analyze(request: AnalyzeRequest):
    """Takes raw textarea content, splits into individual reviews, sends to Gemini,

    and returns results and summary.
    """
    reviews_list = [
        line.strip()
        for line in request.reviews_text.split("\n")
        if line.strip()
    ]

    if not reviews_list:
        raise HTTPException(status_code=400, detail="No reviews provided.")

    try:
        results = analyze_reviews_with_gemini(reviews_list)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Gemini analysis failed: {e}"
        )

    summary = calculate_summary_metrics(results)
    return {"results": results, "summary": summary}


@app.post("/save", response_model=SaveResponse)
def save(request: SaveRequest):
    """Saves analyzed reviews to feedback.db, skipping duplicates on repeat saves."""
    if not request.results:
        raise HTTPException(status_code=400, detail="No results to save.")

    saved_count, duplicates_skipped = save_reviews_to_db(request.results)

    if saved_count == 0:
        message = f"No new reviews saved — all {duplicates_skipped} already existed in {DB_FILE}."
    elif duplicates_skipped > 0:
        message = f"Saved {saved_count} new review(s) to {DB_FILE} ({duplicates_skipped} duplicate(s) skipped)."
    else:
        message = f"Saved {saved_count} reviews to {DB_FILE}"

    return {
        "saved_count": saved_count,
        "duplicates_skipped": duplicates_skipped,
        "message": message,
    }
    

@app.get("/history")
def history():
    """Returns every review ever saved, most recent first — for the 'Saved history' dropdown."""
    return {"reviews": load_all_reviews_from_db()}