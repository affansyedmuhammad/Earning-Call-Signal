from typing import Dict, List, Any
from collections import Counter
import os
from together import Together

# Initialize the Together client
client = Together(api_key=os.getenv("TOGETHER_API_KEY"))

# 1. Classify a single text block using Together.ai
def classify_text_together(text: str) -> str:
    """
    Uses Together.ai to classify `text` as Positive, Neutral, or Negative.
    """
    excerpt = text
    prompt = (
        "Classify the sentiment of this text as Positive, Neutral, or Negative:\n\n"
        f"\"{excerpt}\"\n\nSentiment:"
    )
    resp = client.chat.completions.create(
        model="meta-llama/Llama-3.3-70B-Instruct-Turbo-Free",
        messages=[{"role": "user", "content": prompt}]
    )
    out = resp.choices[0].message.content.strip()
    label = out.split()[0].capitalize()
    return label if label in {"Positive", "Neutral", "Negative"} else "Neutral"

# 2. Optional per-chunk classification (not used here)
def section_sentiment_together(entries: List[Dict[str, str]]) -> Dict[str, Any]:
    """
    Classifies each chunk individually and returns all labels and majority.
    (Kept for backwards compatibility.)
    """
    filtered = [e for e in entries if e.get("speaker", "").lower() != "operator"]
    labels = []
    for entry in filtered:
        labels.append(classify_text_together(entry["text"]))
    majority = Counter(labels).most_common(1)[0][0] if labels else None
    return {"labels": labels, "majority": majority}

# 3. New: collect full section text and classify in two API calls
def extract_together_signals(transcript: Dict[str, Any]) -> Dict[str, Any]:
    """
    Concatenates all Prepared Remarks and Q&A into two strings,
    excludes any Operator entries, then makes exactly two LLM calls
    to classify overall sentiment.
    """
    # Filter out Operator entries
    prepared_entries = [e for e in transcript.get("preparedRemarks", []) if e.get("speaker", "").lower() != "operator"]
    qanda_entries   = [e for e in transcript.get("qanda", [])         if e.get("speaker", "").lower() != "operator"]

    # Concatenate texts for each section
    management_text = "\n".join(e["text"] for e in prepared_entries)
    qa_text         = "\n".join(e["text"] for e in qanda_entries)

    # Single API call per section
    management_sentiment = classify_text_together(management_text)
    qa_sentiment         = classify_text_together(qa_text)
    return {
        "management_sentiment": management_sentiment,
        "qa_sentiment": qa_sentiment
    }
