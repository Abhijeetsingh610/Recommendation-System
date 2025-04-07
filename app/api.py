# app/api.py

from fastapi import FastAPI, Request
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from engine.recommender import get_top_recommendations

app = FastAPI(
    title="SHL Assessment Recommender API",
    description="API to return top SHL assessments for a job description or query using Gemini embeddings.",
    version="1.0.0"
)

# CORS setup (helpful if frontend or external service calls it)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QueryRequest(BaseModel):
    query: str
    top_k: int = 10  # optional, default to 10

@app.get("/")
def read_root():
    return {"message": "SHL Assessment Recommender API is running 🚀"}

@app.post("/recommend")
def recommend_assessments(request: QueryRequest):
    try:
        results = get_top_recommendations(request.query, request.top_k)
        return results.to_dict(orient="records")
    except Exception as e:
        return {"error": str(e)}
