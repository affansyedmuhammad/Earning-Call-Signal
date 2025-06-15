# src/analysis/section_sentiment.py

from typing import Dict, Any, List
from transformers import pipeline

# 1. Initialize the sentiment‐analysis pipeline
#    Uses a financial‐tuned model that returns Positive/Neutral/Negative
SENTIMENT_MODEL = "mrm8488/distilroberta-finetuned-financial-news-sentiment-analysis"
sentiment_analyzer = pipeline(
    "sentiment-analysis",
    model=SENTIMENT_MODEL,
    tokenizer=SENTIMENT_MODEL
)

def section_sentiment(entries: List[Dict[str, str]]) -> Dict[str, float]:
    """
    Given a list of {"speaker":..., "text":...} entries,
    classify each text chunk, then average scores per label.
    Returns a dict with positive_avg, neutral_avg, negative_avg.
    Excludes entries where speaker is "Operator".
    """
    # Filter out entries where speaker is "Operator"
    filtered_entries = [e for e in entries if e.get("speaker", "").lower() != "operator"]
    
    # Extract just the text field from each filtered entry
    texts = [e["text"] for e in filtered_entries]
    if not texts:
        return {"positive_avg": 0.0, "neutral_avg": 0.0, "negative_avg": 0.0}

    results = sentiment_analyzer(texts, truncation=True)
    pos = [r["score"] for r in results if r["label"].lower() == "positive"]
    neu = [r["score"] for r in results if r["label"].lower() == "neutral"]
    neg = [r["score"] for r in results if r["label"].lower() == "negative"]

    return {
        "positive_avg": sum(pos) / len(pos) if pos else 0.0,
        "neutral_avg":  sum(neu) / len(neu) if neu else 0.0,
        "negative_avg": sum(neg) / len(neg) if neg else 0.0,
    }

def extract_nlp_signals(transcript: Dict[str, Any]) -> Dict[str, Any]:
    """
    Given a transcript dict:
      {
        "date": "...",
        "preparedRemarks": [...],
        "qanda": [...]
      }
    returns:
      {
        "management_sentiment": {positive_avg, neutral_avg, negative_avg},
        "qa_sentiment":         {positive_avg, neutral_avg, negative_avg}
      }
    """
    mgmt = section_sentiment(transcript.get("preparedRemarks", []))
    qa   = section_sentiment(transcript.get("qanda", []))
    return {
        "management_sentiment": mgmt,
        "qa_sentiment": qa
    }
