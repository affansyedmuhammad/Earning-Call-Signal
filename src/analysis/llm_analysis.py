from pathlib import Path
from transformers import pipeline, BitsAndBytesConfig, AutoConfig
from .chunker import load_and_chunk
from .signals import split_sections
import json
import re
import torch

# Attempt to load DeepSeek FP8 on GPU, else fallback to Flan-T5 small for CPU
if torch.cuda.is_available():
    # For FP8 quantized DeepSeek, require GPU
    try:
        quant_config = BitsAndBytesConfig(
            load_in_4bit=False,
            load_in_8bit=False,
            fp8=True
        )
        LLM_MODEL = "deepseek-ai/DeepSeek-R1-0528"
        llm = pipeline(
            "text2text-generation",
            model=LLM_MODEL,
            tokenizer=LLM_MODEL,
            quantization_config=quant_config,
            device_map="auto"
        )
    except Exception:
        # Fallback to Flan-T5 small if DeepSeek fails
        LLM_MODEL = "google/flan-t5-small"
        llm = pipeline(
            "text2text-generation",
            model=LLM_MODEL,
            tokenizer=LLM_MODEL,
            device=-1
        )
else:
    # No GPU: use a CPU-friendly model
    LLM_MODEL = "google/flan-t5-small"
    llm = pipeline(
        "text2text-generation",
        model=LLM_MODEL,
        tokenizer=LLM_MODEL,
        device=-1
    )

# Prompt focusing on analysis
PROMPT_TEMPLATE = (
    "You are a financial analytics assistant. "
    "Analyze the {section} section of an earnings call transcript, "
    "providing overall sentiment and three key themes in concise JSON.\n"
    "Excerpt:\n{excerpt}\n"
)

MAX_EXCERPT_CHARS = 1000
MAX_NEW_TOKENS = 80


def filter_boilerplate(chunks: list[str]) -> list[str]:
    """
    Exclude common boilerplate phrases from chunks.
    """
    skip_phrases = [
        "webcast", "investor relations", "replay until", "today's call is nvidia's property"
    ]
    return [text for text in chunks if not any(phrase in text.lower() for phrase in skip_phrases)]


def analyze_section_with_llm(section_texts: list[str], section_name: str) -> dict:
    cleaned = filter_boilerplate(section_texts)
    if not cleaned:
        return {"raw": "", "parsed": None}

    excerpt = ("\n---\n".join(cleaned))[:MAX_EXCERPT_CHARS]
    prompt = PROMPT_TEMPLATE.format(section=section_name, excerpt=excerpt)

    result = llm(
        prompt,
        max_new_tokens=MAX_NEW_TOKENS,
        do_sample=False
    )[0]["generated_text"].strip()

    # Try parsing JSON
    parsed = None
    try:
        start, end = result.find('{'), result.rfind('}') + 1
        parsed_json = result[start:end]
        parsed = json.loads(parsed_json)
    except Exception:
        parsed = None

    return {"raw": result, "parsed": parsed}


def extract_llm_analysis_for_quarter(filepath: Path) -> dict:
    prepared, qa = split_sections(filepath)
    return {
        "management": analyze_section_with_llm(prepared, "Prepared Remarks"),
        "qa": analyze_section_with_llm(qa, "Q&A")
    }


def extract_all_llm_analyses(ticker: str = "NVDA") -> dict:
    analyses = {}
    data_dir = Path(__file__).parents[1] / "data"
    for file in sorted(data_dir.glob(f"{ticker}_*.txt"), reverse=True):
        quarter = file.stem.split("_", 1)[1]
        analyses[quarter] = extract_llm_analysis_for_quarter(file)
    return analyses
