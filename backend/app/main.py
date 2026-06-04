from fastapi import FastAPI

app = FastAPI(
    title="F1 Analysis & Prediction Platform",
    description="Historical F1 analysis + race prediction.",
)


@app.get("/health")
def health_check():
    return {"status": "OK"}
