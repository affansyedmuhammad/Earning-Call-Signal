from fastapi import FastAPI, HTTPException
from pathlib import Path
from typing import Dict, Any, List

from transcript.transcript_client import fetch_and_save_last_n_transcripts
from transcript.transcript_loader import load_json_transcripts
from analysis.signal_extractor import extract_nlp_signals
from analysis.llm_signal_extractor import extract_together_signals

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


@app.get("/signals/{ticker}", response_model=Dict[str, Any])
async def get_signals(ticker: str):
    """
    Returns NLP-based sentiment signals for each quarter of `ticker`.
    Output format:
    {
      "2025Q2": {
        "management_sentiment": {positive_avg, neutral_avg, negative_avg},
        "qa_sentiment":         {positive_avg, neutral_avg, negative_avg}
      },
      ...
    }
    """
    # Load your pre-processed JSON transcripts
    transcripts = load_json_transcripts(ticker.upper())
    if not transcripts:
        raise HTTPException(status_code=404, detail="No transcripts found for ticker")

    # Extract per-section sentiment signals
    signals = {}
    for quarter, transcript in transcripts.items():
        signals[quarter] = extract_nlp_signals(transcript)

    return signals

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
