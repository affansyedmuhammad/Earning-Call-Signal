# src/analysis/llm_section_sentiment.py

from typing import Dict, List, Any
from collections import Counter
from transformers import pipeline

# 1. Initialize the LLM pipeline
LLM_MODEL = "google/flan-t5-small"
llm = pipeline(
    "text2text-generation",
    model=LLM_MODEL,
    tokenizer=LLM_MODEL,
    device=-1
)

def classify_text(text: str) -> str:
    """
    Asks the LLM to classify a single text chunk.
    Returns one of 'Positive', 'Neutral', 'Negative'.
    """
    prompt = (
        "Classify the sentiment of the following text "
        "as Positive, Neutral, or Negative:\n\n"
        f"\"{text}\"\n\nSentiment:"
    )
    out = llm(prompt, max_new_tokens=5, do_sample=False)[0]["generated_text"].strip()
    label = out.split()[0].capitalize()
    return label if label in {"Positive", "Neutral", "Negative"} else "Neutral"

def section_sentiment_llm(entries: List[Dict[str, str]]) -> Dict[str, Any]:
    """
    Given a list of {"speaker":..., "text":...} entries, runs the LLM on each,
    stores all labels, then returns the majority label.
    """
    # Filter out entries where speaker is "Operator"
    filtered_entries = [e for e in entries if e.get("speaker", "").lower() != "operator"]
    
    # Extract just the text field from each filtered entry
    texts = [e["text"] for e in filtered_entries]
    # texts = [e["text"] for e in entries]
    if not texts:
        return {"labels": [], "majority": None}

    # 2. Classify each chunk
    labels = [classify_text(t) for t in texts]

    # 3. Count and pick the majority
    counts = Counter(labels)
    majority, _ = counts.most_common(1)[0]

    return {
        "labels": labels,
        "majority": majority
    }

def extract_llm_signals(transcript: Dict[str, Any]) -> Dict[str, Any]:
    """
    Runs section_sentiment_llm on both Prepared Remarks and Q&A.
    Returns the majority sentiment for each.
    """
    mgmt = section_sentiment_llm(transcript.get("preparedRemarks", []))
    qa   = section_sentiment_llm(transcript.get("qanda", []))
    return {
        "management_sentiment": mgmt,
        "qa_sentiment": qa
    }
