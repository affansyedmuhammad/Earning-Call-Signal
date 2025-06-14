# # in src/analysis/full_llm_analysis.py

# from pathlib import Path
# from transformers import pipeline

# LLM_MODEL = "google/flan-t5-small"   # or any model with a ≥2k‑token window
# llm = pipeline("text2text-generation", model=LLM_MODEL, tokenizer=LLM_MODEL, device=-1)

# def analyze_full_transcript(filepath: Path) -> str:
#     text = filepath.read_text(encoding="utf-8")
#     prompt = (
#         "You are a financial analytics assistant.  "
#         "Here is the full earnings‑call transcript—no excerpts removed:\n\n"
#         f"{text}\n\n"
#         "Now provide:\n"
#         "1) A single overall sentiment (Positive, Neutral, Negative)\n"
#         "2) Three bullet‑point themes raised by management\n"
#         "Respond in JSON with keys \"sentiment\" and \"themes\"."
#     )
#     # The `truncation=True` will silently cut off any tokens past the model limit.
#     out = llm(prompt, max_new_tokens=100, do_sample=False, truncation=True)[0]["generated_text"]
#     return out
