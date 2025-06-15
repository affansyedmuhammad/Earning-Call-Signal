# Earnings Call Signal Analyzer

## What It Does
This application analyzes NVIDIA's earnings call transcripts to extract key signals and insights:
- Strategic focus areas using NLP and frequency analysis
- Management and Q&A sentiment analysis
- Quarter-over-quarter tone changes
- Automated transcript processing and analysis

## Running Locally
1. Clone the repository
2. Ensure Python 3.8 or higher is installed
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Start the FastAPI server:
   ```bash
   uvicorn src.api.main:app --reload --app-dir src
   ```
4. Access the API endpoints:
   - `/getTranscripts/${ticker}`: Get last four Earning Call Transcripts for a specific ticker
   - `/signals/{ticker}`: Get analysis for a specific ticker
   - `/analysis/{ticker}`: View stored analysis results

## AI/NLP Tools Used
- **Sentiment Analysis**: DistilRoBERTa model fine-tuned for financial text
- **Strategic Focus Extraction**: Custom NLP pipeline with:
  - TF-IDF-like approach for term importance
  - N-gram analysis (unigrams, bigrams, trigrams)
  - Keyword-based classification
- **Together.ai API**: Uses Llama-3 for LLM-based text classification (fallback)

## Limitations & Assumptions
- Currently optimized for NVIDIA earnings calls
- Requires structured JSON transcript format
- Strategic focus areas partially rely on predefined keywords
- Sentiment analysis is optimized for financial language
- Real-time analysis limited by API rate limits