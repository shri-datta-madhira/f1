from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

# Read allowed origins from the environment; fall back to local dev.
cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")

app = FastAPI(
    title="F1 Analysis & Prediction Platform",
    description="Historical F1 analysis + race prediction.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["GET"],
    allow_headers=["*"],
)


@app.get("/health")
def health_check():
    return {"status": "OK"}
