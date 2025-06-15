import os
import glob
import json
from typing import Dict, Any

# adjust this if your data folder lives elsewhere
DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data"))

def load_json_transcripts(ticker: str) -> Dict[str, Any]:
    """
    Load all processed .json transcripts for `ticker` from DATA_DIR.
    Returns a dict mapping "YYYYQX" → parsed JSON object.
    """
    pattern = os.path.join(DATA_DIR, f"{ticker}_*.txt")
    transcripts: Dict[str, Any] = {}
    for path in sorted(glob.glob(pattern), reverse=True):
        filename = os.path.basename(path)
        quarter = filename.replace(f"{ticker}_", "").replace(".txt", "")
        with open(path, "r", encoding="utf-8") as f:
            transcripts[quarter] = json.load(f)
    return transcripts