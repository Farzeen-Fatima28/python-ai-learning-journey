import requests
import streamlit as st

# Your FastAPI server (must be running separately via `fastapi run api.py` or `fastapi dev api.py`)
API_BASE_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="Customer Feedback Analyzer", page_icon="📝")

# Keep results across reruns
if "results" not in st.session_state:
    st.session_state.results = None
if "summary" not in st.session_state:
    st.session_state.summary = None

st.title("📝 Customer Feedback Analyzer")
st.write("Paste your customer reviews below, one review per line.")

# ---------- Reviews input ----------
reviews_text = st.text_area(
    "Reviews",
    height=150,
    placeholder="The food was delicious but the delivery took over an hour. Not happy.\n"
    "Amazing taste and the order arrived hot and early. Will order again!\n"
    "Prices have gone up too much for the same small portion.",
)

if st.button("Analyze"):
    if not reviews_text.strip():
        st.warning("Please paste at least one review first.")
    else:
        with st.spinner("Analyzing reviews with Gemini..."):
            try:
                # Backend expects {"reviews_text": "..."} — a single raw string
                response = requests.post(
                    f"{API_BASE_URL}/analyze",
                    json={"reviews_text": reviews_text},
                )

                if response.status_code == 200:
                    data = response.json()
                    st.session_state.results = data.get("results", [])
                    st.session_state.summary = data.get("summary", {})
                else:
                    st.error(
                        f"Error {response.status_code}: {response.json().get('detail', 'Unknown error')}"
                    )
            except requests.exceptions.ConnectionError:
                st.error(
                    "Could not reach the backend. Is `fastapi dev api.py` running?"
                )

# ---------- Results ----------
if st.session_state.results:
    st.subheader("Results")
    st.dataframe(st.session_state.results, width="stretch")

    st.subheader("Summary")
    summary = st.session_state.summary
    if summary:
        col1, col2, col3 = st.columns(3)
        col1.metric("Reviews", summary.get("total_reviews", 0))
        col2.metric("Average score", summary.get("average_score", 0))
        col3.metric("% Positive", f"{summary.get('pct_positive', 0)}%")

        st.info(
            f"**Customers talk most about:** {summary.get('top_theme', 'N/A')}"
        )

    # ---------- Save to database ----------
    if st.button("💾 Save to database"):
        with st.spinner("Saving..."):
            try:
                response = requests.post(
                    f"{API_BASE_URL}/save",
                    json={"results": st.session_state.results},
                )
                if response.status_code == 200:
                    data = response.json()
                    st.success(data.get("message", "Saved successfully!"))
                else:
                    st.error(
                        f"Error {response.status_code}: {response.json().get('detail', 'Unknown error')}"
                    )
            except requests.exceptions.ConnectionError:
                st.error(
                    "Could not reach the backend. Is `fastapi dev api.py` running?"
                )

# ---------- Saved history ----------
with st.expander("📚 Saved history (all reviews in the database)"):
    try:
        response = requests.get(f"{API_BASE_URL}/history")
        if response.status_code == 200:
            history = response.json().get("reviews", [])
            if history:
                st.dataframe(history, width="stretch")
            else:
                st.write("No reviews saved yet.")
        else:
            st.error("Could not load history.")
    except requests.exceptions.ConnectionError:
        st.error(
            "Could not reach the backend. Is `fastapi dev api.py` running?"
        )