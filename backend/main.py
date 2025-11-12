# backend/app.py
from fastapi import FastAPI
from pydantic import BaseModel
from transformers import pipeline
from functools import lru_cache
import asyncio

app = FastAPI(title="⚡ Optimized Text Summarizer API")

# --- Request schema
class SummarizationRequest(BaseModel):
    text: str
    model_name: str = "bart"  # or "t5"
    max_length: int = 130
    min_length: int = 30

# --- Lazy model loading (load only when needed)
@lru_cache(maxsize=2)
def get_model(model_name: str):
    if model_name == "t5":
        return pipeline("summarization", model="t5-base", device=-1)
    else:
        return pipeline("summarization", model="facebook/bart-large-cnn", device=-1)

# --- Efficient chunking (token-aware)
def chunk_text(text, max_chars=1000):
    """Split text efficiently based on character length."""
    text = text.replace("\n", " ").strip()
    if len(text) <= max_chars:
        return [text]
    sentences = text.split(". ")
    chunks, current = [], ""
    for s in sentences:
        if len(current) + len(s) < max_chars:
            current += s + ". "
        else:
            chunks.append(current.strip())
            current = s + ". "
    if current:
        chunks.append(current.strip())
    return chunks

# --- Async summarization endpoint
@app.post("/summarize")
async def summarize_text(request: SummarizationRequest):
    if not request.text.strip():
        return {"error": "Empty text input"}

    summarizer = get_model(request.model_name.lower())
    chunks = chunk_text(request.text)
    results = []

    # Run in async loop to prevent blocking
    loop = asyncio.get_event_loop()
    for chunk in chunks:
        if request.model_name.lower() == "t5":
            chunk = "summarize: " + chunk
        summary = await loop.run_in_executor(
            None,
            lambda: summarizer(
                chunk,
                max_length=request.max_length,
                min_length=request.min_length,
                do_sample=False
            )[0]["summary_text"]
        )
        results.append(summary)

    return {"summary": " ".join(results)}
