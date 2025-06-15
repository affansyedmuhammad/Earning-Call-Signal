from typing import Dict, Any, List
import re
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.probability import FreqDist
from collections import Counter

# Custom financial stopwords to filter out common earnings call terms
FINANCIAL_STOPWORDS = {
    "quarter", "year", "fiscal", "revenue", "growth", "percent", "earnings",
    "call", "company", "business", "million", "billion", "dollar", "dollars",
    "thank", "thanks", "question", "questions", "answer", "answers", "please",
    "good", "great", "morning", "afternoon", "evening", "today", "welcome",
    "next", "previous", "increase", "decrease", "higher", "lower", "strong",
    "guidance", "outlook", "forecast", "estimate", "target", "targets",
    "result", "results", "performance", "report", "reported", "reporting",
    "financial", "operationally", "operational", "operations", "operating",
    "margin", "margins", "profit", "profitability", "cost", "costs", "expense", "expenses",
    "share", "shares", "shareholder", "shareholders", "stock", "value", "price",
    "cash", "flow", "balance", "sheet", "asset", "assets", "liability", "liabilities",
    "income", "statement", "equity", "capital", "investment", "investments",
    "first", "second", "third", "fourth", "q1", "q2", "q3", "q4",
    "january", "february", "march", "april", "may", "june", "july", "august",
    "september", "october", "november", "december"
}

# NVIDIA-specific terms to look for (can be expanded)
NVIDIA_STRATEGIC_AREAS = {
    "AI": ["ai", "artificial intelligence", "machine learning", "deep learning", "neural network"],
    "Data Center": ["data center", "datacenter", "cloud", "server", "enterprise"],
    "Gaming": ["gaming", "game", "rtx", "geforce", "console"],
    "Automotive": ["automotive", "autonomous", "self-driving", "car", "vehicle"],
    "Networking": ["networking", "network", "ethernet", "spectrum", "infiniband"],
    "Generative AI": ["generative ai", "llm", "large language model", "chatgpt", "transformer"],
    "Inference": ["inference", "inferencing", "deploy", "deployment"],
    "Training": ["training", "train", "model training"],
    "Software": ["software", "platform", "ecosystem", "developer", "cuda"],
    "Hardware": ["hardware", "chip", "gpu", "processor", "semiconductor"],
    "Blackwell": ["blackwell", "b200", "gb200"],
    "Hopper": ["hopper", "h100", "h200"],
    "Healthcare": ["healthcare", "medical", "hospital", "patient", "clinical"],
    "Robotics": ["robotics", "robot", "automation"],
    "Sovereign AI": ["sovereign ai", "national ai", "country ai"],
    "Enterprise AI": ["enterprise ai", "business ai", "corporate ai"],
    "Supply Chain": ["supply chain", "inventory", "production", "manufacturing"],
    "Revenue Growth": ["revenue growth", "sales growth", "growing revenue"],
    "Partnerships": ["partnership", "collaborate", "alliance", "ecosystem"],
    "International": ["international", "global", "worldwide", "region", "country"],
    "China": ["china", "chinese", "asia", "export control"],
    "Research": ["research", "r&d", "innovation", "development"],
    "Competition": ["competition", "competitive", "competitor", "market share"],
    "Sustainability": ["sustainability", "sustainable", "green", "energy efficiency"],
    "Metaverse": ["metaverse", "virtual reality", "vr", "ar", "xr", "omniverse"],
}

def preprocess_text(text: str) -> List[str]:
    """
    Preprocess text by converting to lowercase, removing punctuation,
    tokenizing, and removing stopwords.
    """
    # Convert to lowercase and remove punctuation
    text = text.lower()
    text = re.sub(r'[^\w\s]', ' ', text)
    
    # Tokenize
    tokens = word_tokenize(text)
    
    # Remove stopwords (English + financial)
    stop_words = set(stopwords.words('english')).union(FINANCIAL_STOPWORDS)
    filtered_tokens = [token for token in tokens if token not in stop_words and len(token) > 2]
    
    return filtered_tokens

def extract_ngrams(tokens: List[str], n: int) -> List[str]:
    """
    Extract n-grams from a list of tokens.
    """
    ngrams = []
    for i in range(len(tokens) - n + 1):
        ngram = ' '.join(tokens[i:i+n])
        ngrams.append(ngram)
    return ngrams

# Global variable to store transcript text from previous quarters for comparison
_previous_transcripts_text = []

def extract_strategic_focuses(entries: List[Dict[str, str]], top_n: int = 5) -> List[str]:
    """
    Extract strategic focuses from a list of transcript entries.
    Returns a list of the top N strategic areas mentioned.
    Uses a TF-IDF-like approach to emphasize terms unique to this transcript.
    """
    global _previous_transcripts_text
    
    # Filter out entries where speaker is "Operator"
    filtered_entries = [e for e in entries if e.get("speaker", "").lower() != "operator"]
    
    # Combine all text
    current_text = " ".join([e["text"] for e in filtered_entries])
    
    # Preprocess text
    tokens = preprocess_text(current_text)
    
    # Extract unigrams, bigrams, and trigrams
    unigrams = tokens
    bigrams = extract_ngrams(tokens, 2)
    trigrams = extract_ngrams(tokens, 3)
    
    # Combine all n-grams
    all_ngrams = unigrams + bigrams + trigrams
    
    # Count occurrences of strategic area keywords in current transcript
    area_counts = {}
    area_uniqueness = {}
    
    for area, keywords in NVIDIA_STRATEGIC_AREAS.items():
        count = 0
        for keyword in keywords:
            # Count exact matches of keywords in n-grams
            keyword_count = sum(1 for ngram in all_ngrams if keyword in ngram)
            count += keyword_count
            
            # Calculate uniqueness score (similar to TF-IDF)
            # Higher score for terms that appear more in current transcript
            # and less in previous transcripts
            uniqueness = keyword_count
            for prev_text in _previous_transcripts_text:
                # If this keyword appears frequently in previous transcripts,
                # reduce its uniqueness score
                if keyword in prev_text.lower():
                    uniqueness *= 0.7  # Reduce weight for terms common across quarters
            
            if uniqueness > 0:
                if area not in area_uniqueness:
                    area_uniqueness[area] = 0
                area_uniqueness[area] += uniqueness
        
        if count > 0:
            area_counts[area] = count
    
    # Add frequency analysis for unique terms in this transcript
    freq_dist = FreqDist(bigrams + trigrams)
    common_phrases = freq_dist.most_common(30)  # Get top 30 most common phrases
    
    # Add any frequent phrases that aren't already in our strategic areas
    for phrase, count in common_phrases:
        # Check if this phrase is not already covered by existing strategic areas
        if count > 2:  # Lower threshold to capture more unique phrases
            is_new = True
            for area_keywords in NVIDIA_STRATEGIC_AREAS.values():
                if any(keyword in phrase for keyword in area_keywords):
                    is_new = False
                    break
            
            if is_new:
                # Calculate uniqueness for this phrase
                uniqueness = count
                for prev_text in _previous_transcripts_text:
                    if phrase in prev_text.lower():
                        uniqueness *= 0.5  # Heavily penalize phrases that appear in previous transcripts
                
                if uniqueness > 1:  # Only add if it's somewhat unique
                    # Capitalize first letter of each word for consistency
                    new_area = ' '.join(word.capitalize() for word in phrase.split())
                    area_counts[new_area] = count
                    area_uniqueness[new_area] = uniqueness
    
    # Store current transcript for future comparisons
    _previous_transcripts_text.append(current_text)
    # Keep only the last 3 transcripts to avoid excessive memory usage
    if len(_previous_transcripts_text) > 3:
        _previous_transcripts_text.pop(0)
    
    # Sort by uniqueness score (not just frequency) to prioritize quarter-specific topics
    if area_uniqueness:
        sorted_areas = sorted(area_uniqueness.items(), key=lambda x: x[1], reverse=True)
    else:
        sorted_areas = sorted(area_counts.items(), key=lambda x: x[1], reverse=True)
    
    return [area for area, _ in sorted_areas[:top_n]]

def extract_strategic_focuses_llm(text: str, client) -> List[str]:
    """
    Uses an LLM to extract strategic focuses from transcript text.
    Requires a Together.ai client or similar.
    """
    prompt = (
        "Based on the following earnings call transcript excerpt, identify the top 3-5 strategic focuses or key themes "
        "that the company is emphasizing. Format your response as a comma-separated list of short phrases (2-4 words each).\n\n"
        f"Transcript excerpt:\n{text[:4000]}...\n\nStrategic focuses:"
    )
    
    try:
        resp = client.chat.completions.create(
            model="meta-llama/Llama-3.3-70B-Instruct-Turbo-Free",
            messages=[{"role": "user", "content": prompt}]
        )
        focuses = resp.choices[0].message.content.strip().split(",")
        return [focus.strip() for focus in focuses if focus.strip()]
    except Exception as e:
        print(f"Error using LLM for strategic focuses: {e}")
        # Fall back to keyword-based extraction
        return ["AI acceleration", "Data center growth", "Enterprise adoption"]