# from pathlib import Path
# from transformers import pipeline
# from sklearn.feature_extraction.text import TfidfVectorizer
# from .chunker import load_and_chunk

# # Point at your data folder
# DATA_DIR = Path(__file__).parents[1] / "data"

# # Sentiment model (distilled RoBERTa financial-news)
# MODEL_NAME = "mrm8488/distilroberta-finetuned-financial-news-sentiment-analysis"
# sentiment_analyzer = pipeline(
#     "sentiment-analysis",
#     model=MODEL_NAME,
#     tokenizer=MODEL_NAME
# )

# def split_sections(filepath: Path):
#     """
#     Splits a transcript into two parts:
#       - prepared remarks (executive speeches before Q&A)
#       - Q&A section (analyst questions and responses)
#     Detection uses specific Operator prompts indicating the start of Q&A.
#     """
#     chunks = load_and_chunk(filepath)
#     prepared, qa = [], []
#     in_qa = False

#     for speaker, body in chunks:
#         lower = body.lower()
#         # Detect start of Q&A: look for explicit First/Next question prompts
#         if speaker == "Operator" and ("first question" in lower or "question comes" in lower):
#             in_qa = True
#             continue

#         # Before Q&A, collect executive remarks (skip Operator)
#         if not in_qa:
#             if speaker != "Operator":
#                 prepared.append(body)
#         else:
#             # After Q&A start, collect all non-Operator dialogue
#             if speaker != "Operator":
#                 qa.append(body)

#     return prepared, qa


# def analyze_section(texts: list[str]) -> dict:
#     """
#     Runs sentiment on a list of chunks and returns average scores.
#     """
#     if not texts:
#         return {"chunks": 0, "positive_avg": 0, "negative_avg": 0, "neutral_avg": 0}

#     results = sentiment_analyzer(texts, truncation=True)
#     pos = [r["score"] for r in results if r["label"] == "positive"]
#     neg = [r["score"] for r in results if r["label"] == "negative"]
#     neu = [r["score"] for r in results if r["label"] == "neutral"]

#     return {
#         "chunks": len(texts),
#         "positive_avg": sum(pos) / len(pos) if pos else 0,
#         "negative_avg": sum(neg) / len(neg) if neg else 0,
#         "neutral_avg": sum(neu) / len(neu) if neu else 0
#     }


# def extract_themes(texts: list[str], top_n: int = 5) -> list[str]:
#     """
#     Uses TF-IDF to extract top_n keywords/ngrams.
#     Returns empty list if no vocabulary is found.
#     """
#     if not texts:
#         return []
#     try:
#         vec = TfidfVectorizer(
#             ngram_range=(1, 2),
#             stop_words="english",
#             max_features=500
#         )
#         X = vec.fit_transform(texts)
#         scores = zip(vec.get_feature_names_out(), X.sum(axis=0).A1)
#         top = sorted(scores, key=lambda x: x[1], reverse=True)[:top_n]
#         return [term for term, _ in top]
#     except ValueError:
#         # no valid terms found
#         return []


# def extract_signals_for_quarter(filepath: Path) -> dict:
#     """
#     Extracts signals for one transcript file:
#       - management_sentiment
#       - qa_sentiment
#       - strategic_focuses
#     """
#     prepared, qa = split_sections(filepath)
#     return {
#         "management_sentiment": analyze_section(prepared),
#         "qa_sentiment": analyze_section(qa),
#         "strategic_focuses": extract_themes(prepared, top_n=5)
#     }


# def extract_all_signals(ticker: str = "NVDA") -> dict:
#     """
#     Processes all transcripts and computes QoQ tone changes.
#     """
#     signals = {}
#     files = sorted(DATA_DIR.glob(f"{ticker}_*.txt"), reverse=True)
#     quarters = [f.stem.split("_", 1)[1] for f in files]

#     for f, tag in zip(files, quarters):
#         signals[tag] = extract_signals_for_quarter(f)

#     # Compute quarter-over-quarter positive tone change
#     qoq = {}
#     for i in range(len(quarters) - 1):
#         cur, prev = quarters[i], quarters[i + 1]
#         cur_avg = signals[cur]["management_sentiment"]["positive_avg"]
#         prev_avg = signals[prev]["management_sentiment"]["positive_avg"]
#         qoq[f"{prev}_to_{cur}"] = cur_avg - prev_avg

#     return {"signals": signals, "qoq_tone_change": qoq}
