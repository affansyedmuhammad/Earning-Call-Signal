from fastapi import FastAPI, HTTPException
from pathlib import Path

from transcript.transcript_client import fetch_and_save_last_n_transcripts
from transcript.transcript_loader import load_json_transcripts

app = FastAPI(
    title="Earnings Call Analyzer",
    description="Fetch & analyze NVIDIA earnings call transcripts",
    version="0.1.0"
)

@app.get("/")
async def read_root():
    return {"message": "Welcome to your Earnings Call Analyzer!"}

@app.get("/saveTranscripts/{ticker}", summary="Get last 4 transcripts")
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

@app.get("/getTranscripts/{ticker}")
async def get_transcripts(ticker: str):
    data = load_json_transcripts(ticker.upper())
    if not data:
        raise HTTPException(404, "No transcripts found")
    return data


# @app.get("/sentiment/{ticker}", summary="Analyze transcript sentiments")
# async def sentiment_report(ticker: str):
#     """
#     Runs sentiment analysis across all saved transcripts for `ticker`.
#     """
#     try:
#         report = analyze_all_transcripts(ticker.upper())
#         return {"ticker": ticker.upper(), "sentiment": report}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

# @app.get("/signals/{ticker}", summary="Extract all signals for a ticker")
# async def signals_report(ticker: str):
#     """
#     Returns management vs Q&A sentiment, strategic themes per quarter,
#     and quarter‑over‑quarter tone changes.
#     """
#     try:
#         return extract_all_signals(ticker.upper())
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

# @app.get("/llm_analysis/{ticker}", summary="LLM‑based sentiment & theme analysis")
# async def llm_report(ticker: str):
#     """
#     Uses an open‑source LLM (Flan‑T5) to summarize sentiment and extract 3 themes
#     for both the Prepared Remarks and Q&A sections of each quarter’s transcript.
#     """
#     try:
#         analysis = extract_all_llm_analyses(ticker.upper())
#         return {"ticker": ticker.upper(), "llm_analysis": analysis}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

# @app.get("/analysis/full/{ticker}")
# async def full_transcript_analysis(ticker: str):
#     try:
#         # assumes files are named TICKER_YYYYQn.txt
#         latest = sorted(Path("src/data").glob(f"{ticker}_*.txt"))[-1]
#         result = analyze_full_transcript(latest)
#         return {"ticker": ticker, "analysis": result}
#     except Exception as e:
#         raise HTTPException(500, str(e))


# @app.get("/analysis/long/{ticker}")
# async def long_transcript_analysis(ticker: str):
#     try:
#         latest = sorted(Path("src/data").glob(f"{ticker}_*.txt"))[-1]
#         return analyze_full_long(latest)
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))
