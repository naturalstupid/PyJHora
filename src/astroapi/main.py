"""FastAPI application exposing horoscope computation endpoints."""
from fastapi import FastAPI, HTTPException

from .models import ChartRequest
from .services import compute_chart

app = FastAPI(title="AstroCal API")

@app.get("/health")
def health_check():
    """Simple health check endpoint."""
    return {"status": "ok"}

@app.post("/chart")
def generate_chart(request: ChartRequest):
    """Compute a Vedic horoscope and return detailed data."""
    try:
        return compute_chart(request)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))

