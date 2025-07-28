from fastapi import FastAPI, HTTPException
from datetime import datetime
from pydantic import BaseModel, Field
from typing import List, Optional
import time

app = FastAPI(
    title="Indonesia Tourism RecSys API",
    description="AI-powered tourism recommendations",
    version="1.0.0"
)

# Pydantic Models
class RecommendationRequest(BaseModel):
    place_id: int = Field(..., example=1)
    user_preferences: Optional[List[str]] = Field(default=[], example=["beach", "family"])
    num_recommendations: int = Field(default=5, ge=1, le=20)

class Place(BaseModel):
    place_id: int
    place_name: str
    category: str
    city: str
    rating: float
    description: Optional[str] = None

class RecommendationResponse(BaseModel):
    recommendations: List[Place]
    source_place_id: int
    total: int
    generated_at: datetime
    model_version: str = "v1.0-dummy"

# Dummy Database
PLACES_DB = [
    {"place_id": 1, "place_name": "Pantai Kuta", "category": "Beach", "city": "Bali", "rating": 4.5, "description": "Famous beach with surfing"},
    {"place_id": 2, "place_name": "Candi Borobudur", "category": "Temple", "city": "Yogyakarta", "rating": 4.8, "description": "Ancient Buddhist temple"},
    {"place_id": 3, "place_name": "Raja Ampat", "category": "Island", "city": "Papua", "rating": 4.9, "description": "Diving paradise"},
    {"place_id": 4, "place_name": "Kawah Ijen", "category": "Mountain", "city": "Banyuwangi", "rating": 4.7, "description": "Blue fire crater"},
    {"place_id": 5, "place_name": "Tanah Lot", "category": "Temple", "city": "Bali", "rating": 4.4, "description": "Sea temple"},
    {"place_id": 6, "place_name": "Gili Trawangan", "category": "Island", "city": "Lombok", "rating": 4.6, "description": "Party island"},
    {"place_id": 7, "place_name": "Bromo", "category": "Mountain", "city": "East Java", "rating": 4.7, "description": "Active volcano"},
]

@app.get("/", tags=["General"])
def root():
    """API Information"""
    return {
        "message": "Indonesia Tourism RecSys API",
        "version": "1.0.0",
        "endpoints": {
            "docs": "/docs",
            "health": "/health",
            "recommendations": "/api/v1/recommend"
        }
    }

@app.get("/health", tags=["General"])
def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "tourism-recsys",
        "database": "connected",
        "model": "loaded"
    }

@app.post("/api/v1/recommend", response_model=RecommendationResponse, tags=["Recommendations"])
def get_recommendations(request: RecommendationRequest):
    """Get personalized tourism recommendations"""
    
    # Validate place exists
    source = next((p for p in PLACES_DB if p["place_id"] == request.place_id), None)
    if not source:
        raise HTTPException(status_code=404, detail=f"Place {request.place_id} not found")
    
    # Filter based on preferences
    filtered = PLACES_DB.copy()
    if request.user_preferences:
        if "beach" in request.user_preferences:
            filtered = [p for p in filtered if p["category"] in ["Beach", "Island"]]
        if "temple" in request.user_preferences:
            filtered = [p for p in filtered if p["category"] == "Temple"]
        if "mountain" in request.user_preferences:
            filtered = [p for p in filtered if p["category"] == "Mountain"]
    
    # Remove source place
    filtered = [p for p in filtered if p["place_id"] != request.place_id]
    
    # Get top N by rating
    filtered.sort(key=lambda x: x["rating"], reverse=True)
    recommendations = filtered[:request.num_recommendations]
    
    return RecommendationResponse(
        recommendations=[Place(**p) for p in recommendations],
        source_place_id=request.place_id,
        total=len(recommendations),
        generated_at=datetime.utcnow()
    )

@app.get("/api/v1/places", tags=["Places"])
def list_places(
    category: Optional[str] = None,
    city: Optional[str] = None,
    min_rating: Optional[float] = None
):
    """List all places with optional filters"""
    results = PLACES_DB.copy()
    
    if category:
        results = [p for p in results if p["category"].lower() == category.lower()]
    if city:
        results = [p for p in results if p["city"].lower() == city.lower()]
    if min_rating:
        results = [p for p in results if p["rating"] >= min_rating]
    
    return {
        "places": results,
        "total": len(results),
        "filters": {
            "category": category,
            "city": city,
            "min_rating": min_rating
        }
    }

@app.get("/api/v1/places/{place_id}", tags=["Places"])
def get_place_detail(place_id: int):
    """Get detailed information about a place"""
    place = next((p for p in PLACES_DB if p["place_id"] == place_id), None)
    if not place:
        raise HTTPException(status_code=404, detail="Place not found")
    return place

@app.get("/api/v1/stats", tags=["Statistics"])
def get_statistics():
    """Get API statistics"""
    return {
        "total_places": len(PLACES_DB),
        "categories": list(set(p["category"] for p in PLACES_DB)),
        "cities": list(set(p["city"] for p in PLACES_DB)),
        "avg_rating": sum(p["rating"] for p in PLACES_DB) / len(PLACES_DB),
        "top_rated": max(PLACES_DB, key=lambda x: x["rating"])
    }
