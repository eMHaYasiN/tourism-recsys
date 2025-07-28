from fastapi import FastAPI
from datetime import datetime
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI(title="Tourism RecSys API", version="1.0.0")

# Models
class RecommendationRequest(BaseModel):
    place_id: int
    num_recommendations: int = 5

class Place(BaseModel):
    place_id: int
    place_name: str
    category: str
    city: str
    rating: float

# Dummy data
DUMMY_PLACES = [
    {"place_id": 1, "place_name": "Pantai Kuta", "category": "Beach", "city": "Bali", "rating": 4.5},
    {"place_id": 2, "place_name": "Borobudur", "category": "Temple", "city": "Yogyakarta", "rating": 4.8},
    {"place_id": 3, "place_name": "Raja Ampat", "category": "Island", "city": "Papua", "rating": 4.9},
]

@app.get("/")
def root():
    return {"message": "Tourism RecSys API", "docs": "/docs"}

@app.get("/health")
def health():
    return {"status": "healthy", "time": datetime.utcnow().isoformat()}

@app.post("/recommend")
def recommend(request: RecommendationRequest):
    return {
        "recommendations": DUMMY_PLACES[:request.num_recommendations],
        "source_place_id": request.place_id,
        "count": len(DUMMY_PLACES[:request.num_recommendations])
    }

@app.get("/places/popular")
def popular_places(limit: int = 5):
    return {"places": DUMMY_PLACES[:limit]}
