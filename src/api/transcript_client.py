import os
import requests
from datetime import datetime
from dotenv import load_dotenv

# load your API‑Ninjas key
load_dotenv()
API_KEY = os.getenv("API_NINJAS_KEY")
BASE_URL = "https://api.api-ninjas.com/v1/earningstranscript"

# point at your existing data folder under src/data/
DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data"))
os.makedirs(DATA_DIR, exist_ok=True)

def get_last_n_quarters(n: int = 4):
    """
    Returns a list of (year, quarter) tuples for the last n quarters,
    newest first. E.g. [(2025,2), (2025,1), (2024,4), (2024,3)].
    """
    today = datetime.today()
    year = today.year
    quarter = (today.month - 1) // 3 + 1

    quarters = []
    for _ in range(n):
        quarters.append((year, quarter))
        quarter -= 1
        if quarter == 0:
            quarter = 4
            year -= 1

    return quarters

def fetch_transcript(ticker: str, year: int, quarter: int) -> str:
    """
    Calls API‑Ninjas and RETURNS the raw transcript text.
    Raises an HTTPError on failure.
    """
    params = {"ticker": ticker, "year": year, "quarter": quarter}
    headers = {"X-Api-Key": API_KEY}
    resp = requests.get(BASE_URL, params=params, headers=headers, timeout=10)
    resp.raise_for_status()
    return resp.text

def fetch_and_save_transcript(ticker: str, year: int, quarter: int) -> str:
    """
    Fetches a single transcript and writes it to src/data/.
    Returns the absolute filepath.
    """
    text = fetch_transcript(ticker, year, quarter)
    filename = f"{ticker}_{year}Q{quarter}.txt"
    filepath = os.path.join(DATA_DIR, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(text)
    return filepath

def fetch_and_save_last_n_transcripts(ticker: str = "NVDA", n: int = 4) -> dict:
    """
    Fetches & saves the last n quarters’ transcripts for `ticker`.
    Returns a dict mapping "YYYYQ#" → filepath or error string.
    """
    results = {}
    for year, q in get_last_n_quarters(n):
        key = f"{year}Q{q}"
        try:
            path = fetch_and_save_transcript(ticker, year, q)
            results[key] = path
        except Exception as e:
            results[key] = f"Error: {e}"
    return results
