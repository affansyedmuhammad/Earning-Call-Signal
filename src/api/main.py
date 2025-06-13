from fastapi import FastAPI, HTTPException
from api.transcript_client import fetch_and_save_last_n_transcripts
from analysis.sentiment import analyze_all_transcripts

app = FastAPI(
    title="Earnings Call Analyzer",
    description="Fetch & analyze NVIDIA earnings call transcripts",
    version="0.1.0"
)

@app.get("/")
async def read_root():
    return {"message": "Welcome to your Earnings Call Analyzer!"}

@app.get("/transcripts/{ticker}", summary="Get last 4 transcripts")
async def get_nvidia_transcripts(ticker: str):
    """
    Fetches the last 4 quarters transcripts for NVDA via API Ninjas,
    saves them under src/data/, and returns their file paths (or errors).
    """
    try:
        results = fetch_and_save_last_n_transcripts(ticker.upper(), 4)
        return {"ticker": ticker.upper(), "results": results}
    except Exception as e:
        # fallback for any unexpected error
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/sentiment/{ticker}", summary="Analyze transcript sentiments")
async def sentiment_report(ticker: str):
    """
    Runs sentiment analysis across all saved transcripts for `ticker`.
    """
    try:
        report = analyze_all_transcripts(ticker.upper())
        return {"ticker": ticker.upper(), "sentiment": report}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))