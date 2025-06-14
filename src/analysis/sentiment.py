# from pathlib import Path
# from transformers import pipeline
# from .chunker import load_and_chunk

# # Point at your data folder (same one your /transcripts endpoint writes to)
# DATA_DIR = Path(__file__).parents[1] / "data"

# # Point at the model you want to use (see Hugging Face)
# MODEL_NAME = "mrm8488/distilroberta-finetuned-financial-news-sentiment-analysis"

# # Initialize the sentiment pipeline with explicit model and tokenizer
# sentiment_analyzer = pipeline(
#     "sentiment-analysis",
#     model=MODEL_NAME,
#     tokenizer=MODEL_NAME
# )

# def analyze_transcript(filepath: Path) -> dict:
#     """
#     Reads a transcript file, chunks it by speaker-turn,
#     runs sentiment on each chunk, and returns a summary.
#     """
#     speaker_chunks = load_and_chunk(filepath)
#     texts = [body for _, body in speaker_chunks]

#     # run sentiment on each chunk
#     results = sentiment_analyzer(texts, truncation=True)

#     # separate scores by label (labels are 'positive', 'neutral', 'negative')
#     pos_scores = [r["score"] for r in results if r["label"] == "positive"]
#     neg_scores = [r["score"] for r in results if r["label"] == "negative"]
#     neu_scores = [r["score"] for r in results if r["label"] == "neutral"]

#     return {
#         "file": filepath.name,
#         "chunks": len(texts),
#         "positive_avg": sum(pos_scores) / len(pos_scores) if pos_scores else 0,
#         "negative_avg": sum(neg_scores) / len(neg_scores) if neg_scores else 0,
#         "neutral_avg": sum(neu_scores) / len(neu_scores) if neu_scores else 0,
#         "detailed": [
#             {
#                 "speaker": speaker_chunks[i][0],
#                 # "text": speaker_chunks[i][1],
#                 "label": results[i]["label"],
#                 "score": results[i]["score"]
#             }
#             for i in range(len(results))
#         ]
#     }

# def analyze_all_transcripts(ticker: str = "NVDA") -> dict:
#     """
#     Finds all files matching TICKER_*.txt in DATA_DIR (newest first),
#     analyzes each, and returns a mapping quarter→sentiment summary.
#     """
#     summaries = {}
#     for file in sorted(DATA_DIR.glob(f"{ticker}_*.txt"), reverse=True):
#         quarter_tag = file.stem.split("_", 1)[1]
#         summaries[quarter_tag] = analyze_transcript(file)
#     return summaries
