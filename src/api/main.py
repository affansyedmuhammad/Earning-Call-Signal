from fastapi import FastAPI, HTTPException
from api.transcript_client import fetch_and_save_last_n_transcripts

app = FastAPI(
    title="Earnings Call Analyzer",
    description="Fetch & analyze NVIDIA earnings call transcripts",
    version="0.1.0"
)

@app.get("/")
async def read_root():
    return {"message": "Welcome to your Earnings Call Analyzer!"}

@app.get("/transcripts/nvidia", summary="Get last 4 NVIDIA transcripts")
async def get_nvidia_transcripts():
    """
    Fetches the last 4 quarters’ transcripts for NVDA via API‑Ninjas,
    saves them under src/data/, and returns their file paths (or errors).
    """
    try:
        results = fetch_and_save_last_n_transcripts("NVDA", 4)
        return {"ticker": "NVDA", "results": results}
    except Exception as e:
        # fallback for any unexpected error
        raise HTTPException(status_code=500, detail=str(e))
