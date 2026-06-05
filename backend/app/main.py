from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import check_connection

app = FastAPI(
    title="F1 Analysis & Prediction Platform",
    description="Historical F1 analysis + race prediction.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["GET"],
    allow_headers=["*"],
)


@app.get("/health")
def health_check():
    return {"status": "OK"}

@app.get("/db-check")
def db_check():
    check_connection()
    return {"status": "Database connection successful"}