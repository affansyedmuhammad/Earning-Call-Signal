# src/analysis/section_sentiment.py

from typing import Dict, Any, List
from transformers import pipeline
from .strategic_focus import extract_strategic_focuses

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
    classify each text chunk (excluding "Operator"), then average scores per label.
    Returns a dict with positive_avg, neutral_avg, negative_avg.
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
    Given a transcript dict with keys:
      {
        "date": "...",
        "preparedRemarks": [...],
        "qanda": [...]
      }
    returns per-section sentiment and strategic focuses:
      {
        "management_sentiment": {...},
        "qa_sentiment":         {...},
        "strategic_focuses":    ["focus1", "focus2", ...]
      }
    """
    mgmt = section_sentiment(transcript.get("preparedRemarks", []))
    qa   = section_sentiment(transcript.get("qanda", []))
    
    # Extract strategic focuses from both prepared remarks and Q&A sections
    # This provides a more comprehensive view of strategic focuses for each quarter
    prepared_remarks = transcript.get("preparedRemarks", [])
    qanda_section = transcript.get("qanda", [])
    
    # Filter Q&A to only include company executives' responses (not analysts' questions)
    # This assumes executives are not "Operator" and not names that typically ask questions
    exec_responses = []
    for entry in qanda_section:
        speaker = entry.get("speaker", "").lower()
        if speaker != "operator" and not any(name in speaker.lower() for name in ["analyst", "research", "capital", "securities", "bank", "morgan", "goldman", "sachs", "ubs", "citi", "deutsche", "barclays"]):
            exec_responses.append(entry)
    
    # Combine prepared remarks and executive Q&A responses for strategic focus extraction
    all_exec_content = prepared_remarks + exec_responses
    focuses = extract_strategic_focuses(all_exec_content, top_n=5)
    
    return {
        "management_sentiment": mgmt,
        "qa_sentiment": qa,
        "strategic_focuses": focuses
    }


def compute_qoq_tone(signals: Dict[str, Any]) -> Dict[str, Any]:
    """
    Given per-quarter signals mapping:
      {
        "2024Q3": {"management_sentiment": {...}, "qa_sentiment": {...}},
        "2024Q4": {...},
        ...
      }
    Computes quarter-over-quarter deltas on positive_avg for both sections:
      {
        "2024Q3_to_2024Q4": {"management_tone_shift": x, "qa_tone_shift": y},
        ...
      }
    """
    # Sort quarters chronologically by year and quarter number
    def sort_key(q: str):
        year, qnum = q.split('Q')
        return (int(year), int(qnum))

    quarters = sorted(signals.keys(), key=sort_key)
    qoq: Dict[str, Dict[str, float]] = {}
    for i in range(1, len(quarters)):
        prev_q = quarters[i-1]
        cur_q  = quarters[i]
        prev_sig = signals[prev_q]["management_sentiment"]["positive_avg"]
        cur_sig  = signals[cur_q]["management_sentiment"]["positive_avg"]
        prev_qa  = signals[prev_q]["qa_sentiment"]["positive_avg"]
        cur_qa   = signals[cur_q]["qa_sentiment"]["positive_avg"]

        qoq[f"{prev_q}_to_{cur_q}"] = {
            "management_tone_shift": cur_sig - prev_sig,
            "qa_tone_shift":         cur_qa  - prev_qa
        }

    return qoq


def extract_all_signals(transcripts: Dict[str, Any]) -> Dict[str, Any]:
    """
    Given a dict of transcripts per quarter:
      { "2024Q3": {...}, "2024Q4": {...}, ... }
    Returns:
      {
        "signals": { ... per-quarter sentiment and strategic focuses ... },
        "qoq_tone_change": { ... deltas ... }
      }
    """
    signals: Dict[str, Any] = {}
    for quarter, transcript in transcripts.items():
        signals[quarter] = extract_nlp_signals(transcript)

    qoq_changes = compute_qoq_tone(signals)
    return {
        "signals": signals,
        "qoq_tone_change": qoq_changes
    }
