# from pathlib import Path
# from transformers import pipeline
# import json

# # 1. Initialize a small, efficient LLM
# LLM_MODEL = "google/flan-t5-small"
# llm = pipeline(
#     "text2text-generation",
#     model=LLM_MODEL,
#     tokenizer=LLM_MODEL,
#     device=-1
# )

# # 2. Utility to chunk long transcripts into manageable pieces
# def chunkify(text: str, max_chars: int = 2000):
#     """
#     Split text into chunks of approx max_chars on paragraph boundaries.
#     """
#     paras = text.split("\n\n")
#     chunks, cur = [], ""
#     for p in paras:
#         if len(cur) + len(p) + 2 > max_chars:
#             chunks.append(cur.strip())
#             cur = p
#         else:
#             cur = cur + "\n\n" + p if cur else p
#     if cur:
#         chunks.append(cur.strip())
#     return chunks

# # 3. Summarize each chunk briefly
# def summarize_chunk(chunk: str) -> str:
#     prompt = f"Summarize this earnings call excerpt in one sentence:\n{chunk}\nSummary:"
#     result = llm(prompt, max_new_tokens=50, do_sample=False)[0]["generated_text"].strip()
#     return result.strip()

# # 4. Fuse summaries into overall sentiment and themes
# def synthesize_summaries(summaries: list[str]) -> dict:
#     joined = "\n".join(f"- {s}" for s in summaries)
#     prompt = (
#         "You are a financial analytics assistant. Given the following bullet summaries of an earnings call:\n"
#         f"{joined}\n"
#         "Provide JSON with keys:\n"
#         "  \"sentiment\": one of \"Positive\", \"Neutral\", \"Negative\"\n"
#         "  \"themes\": list of 3 key themes mentioned by management\n"
#         "Output ONLY the JSON object."
#     )
#     result = llm(prompt, max_new_tokens=100, do_sample=False)[0]["generated_text"].strip()
#     try:
#         return json.loads(result)
#     except json.JSONDecodeError:
#         # fallback: return raw
#         return {"raw": result}

# # 5. Main entry: analyze full transcript file
# def analyze_full_long(filepath: Path) -> dict:
#     text = filepath.read_text(encoding="utf-8")
#     chunks = chunkify(text)
#     # Summarize in parallel
#     summaries = [summarize_chunk(c) for c in chunks]

#     # Get overall analysis
#     overall = synthesize_summaries(summaries)
#     return overall

# # Example usage:
# # from chain_llm_analysis import analyze_full_long
# # analyze_full_long(Path("src/data/NVDA_2025Q2.txt"))
