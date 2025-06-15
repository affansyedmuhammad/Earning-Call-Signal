from fastapi import FastAPI, HTTPException
from pathlib import Path
from typing import Dict, Any, List
from fastapi.middleware.cors import CORSMiddleware
import os
import glob
import json


from transcript.transcript_client import fetch_and_save_last_n_transcripts
from transcript.transcript_loader import load_json_transcripts
from analysis.signal_extractor import extract_all_signals
from analysis.llm_signal_extractor import extract_together_signals

app = FastAPI(
    title="Earnings Call Analyzer",
    description="Fetch & analyze NVIDIA earnings call transcripts",
    version="0.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost",        # React dev server
        "http://127.0.0.1",        # sometimes the same
        # or simply "*" for _all_ origins (dev only!)
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data"))

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


@app.get("/signals/{ticker}", response_model=Dict[str, Any])
async def get_signals(ticker: str):
    """
    Returns section-level sentiment, strategic focuses, and quarter-over-quarter tone shifts for given ticker.
    {
      "signals": { 
        <quarter>: {
          "management_sentiment": {...},
          "qa_sentiment": {...},
          "strategic_focuses": ["focus1", "focus2", ...]
        }, 
        ... 
      },
      "qoq_tone_change": { <prev_to_cur>: {...deltas...}, ... }
    }
    """
    # Load structured transcripts JSON
    transcripts = load_json_transcripts(ticker.upper())
    if not transcripts:
        raise HTTPException(status_code=404, detail="No transcripts found for ticker")

    # Extract NLP signals and QoQ changes
    result = extract_all_signals(ticker.upper(), transcripts)
    return result


@app.get("/analysis/{ticker}", response_model=dict)
async def get_analysis(ticker: str):
    pattern = os.path.join(DATA_DIR, f"analysis_{ticker.upper()}.txt")
    result: Dict[str, Any] = {}
    for path in sorted(glob.glob(pattern), reverse=True):
        filename = os.path.basename(path)
        with open(path, "r", encoding="utf-8") as f:
            result = json.load(f)
    return result

@app.get("/signals_llm/{ticker}", response_model=Dict[str, Any])
async def get_together_signals(ticker: str):
    """
    LLM‑based sentiment for each quarter, powered by Together.ai.
    """
    transcripts = load_json_transcripts(ticker.upper())
    if not transcripts:
        raise HTTPException(404, "No transcripts found")

    out = {}
    for quarter, tr in transcripts.items():
        out[quarter] = extract_together_signals(tr)
    return out

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        app_dir="src/api"
    )