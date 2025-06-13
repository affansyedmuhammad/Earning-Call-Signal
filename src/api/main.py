from fastapi import FastAPI

app = FastAPI(
    title="Earnings Call Analyzer",
    description="Fetch & analyze NVIDIA earnings call transcripts",
    version="0.1.0"
)

@app.get("/")
async def read_root():
    return {"message": "Welcome to your Earnings Call Analyzer!"}
