from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import numpy as np
import joblib
import os
from pathlib import Path

app = FastAPI(title="AI Crop ML Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load models
MODEL_DIR = Path("models")
CROP_MODEL_PATH = MODEL_DIR / "crop_recommender.pkl"
DISEASE_MODEL_PATH = MODEL_DIR / "disease_classifier.pkl"

crop_model = None
disease_model = None

if CROP_MODEL_PATH.exists():
    crop_model = joblib.load(CROP_MODEL_PATH)
    print(f"Loaded crop recommendation model from {CROP_MODEL_PATH}")

if DISEASE_MODEL_PATH.exists():
    try:
        disease_model = joblib.load(DISEASE_MODEL_PATH)
        print(f"Loaded disease classification model from {DISEASE_MODEL_PATH}")
    except Exception as e:
        print(f"Failed to load disease model: {e}. Falling back to rule-based diagnosis.")
        disease_model = None


class PredictionRequest(BaseModel):
    latitude: float
    longitude: float
    area: float
    soil_ph: Optional[float] = None
    soil_n: Optional[float] = None
    soil_p: Optional[float] = None
    soil_k: Optional[float] = None
    last_crop: Optional[str] = None
    irrigation_available: bool = False
    preferences: Dict[str, Any] = {}


@app.get("/")
def root():
    return {"message": "AI Crop ML Service", "status": "running"}


@app.get("/health")
def health():
    return {"status": "healthy", "models_loaded": {
        "crop_model": crop_model is not None,
        "disease_model": disease_model is not None
    }}


@app.post("/predict")
def predict(request: PredictionRequest):
    """
    Predict crop recommendations based on field data
    """
    if crop_model is None:
        # Fallback to rule-based recommendations
        return get_rule_based_recommendations(request)
    
    try:
        # Prepare features
        features = prepare_features(request)
        
        # Get predictions
        predictions = crop_model.predict_proba([features])
        
        # Get top crops
        crop_classes = crop_model.classes_
        top_indices = np.argsort(predictions[0])[-3:][::-1]
        
        recommendations = []
        for idx in top_indices:
            crop = crop_classes[idx]
            score = float(predictions[0][idx])
            yield_est = estimate_yield(crop, request)
            profit_est = estimate_profit(crop, yield_est)
            sustainability = calculate_sustainability(crop, request)
            explanation = generate_explanation(crop, request, score)
            
            recommendations.append({
                "crop": crop,
                "suitability_score": score,
                "expected_yield": yield_est,
                "expected_profit": profit_est,
                "sustainability_score": sustainability,
                "explanation": explanation
            })
        
        return {"recommendations": recommendations}
    
    except Exception as e:
        print(f"Error in prediction: {e}")
        return get_rule_based_recommendations(request)


def prepare_features(request: PredictionRequest) -> np.ndarray:
    """Prepare feature vector for model"""
    # Default values if not provided
    soil_ph = request.soil_ph if request.soil_ph is not None else 7.0
    soil_n = request.soil_n if request.soil_n is not None else 50.0
    soil_p = request.soil_p if request.soil_p is not None else 30.0
    soil_k = request.soil_k if request.soil_k is not None else 40.0
    
    # Feature vector: [lat, lon, area, ph, N, P, K, irrigation]
    features = np.array([
        request.latitude,
        request.longitude,
        request.area,
        soil_ph,
        soil_n,
        soil_p,
        soil_k,
        1.0 if request.irrigation_available else 0.0
    ])
    
    return features


def estimate_yield(crop: str, request: PredictionRequest) -> float:
    """Estimate yield based on crop and conditions"""
    # Base yields (tons/ha) - simplified
    base_yields = {
        "wheat": 3.5,
        "rice": 4.0,
        "maize": 4.5,
        "cotton": 1.2,
        "sugarcane": 70.0,
        "potato": 25.0,
        "tomato": 30.0,
        "onion": 20.0,
    }
    
    base = base_yields.get(crop.lower(), 3.0)
    
    # Adjust based on soil quality
    if request.soil_ph:
        if 6.0 <= request.soil_ph <= 7.5:
            base *= 1.1
        elif request.soil_ph < 5.0 or request.soil_ph > 8.5:
            base *= 0.8
    
    if request.irrigation_available:
        base *= 1.15
    
    return round(base, 2)


def estimate_profit(crop: str, yield_est: float) -> float:
    """Estimate profit per hectare"""
    # Market prices (₹/ton) - simplified
    prices = {
        "wheat": 20000,
        "rice": 18000,
        "maize": 15000,
        "cotton": 6000,
        "sugarcane": 3000,
        "potato": 15000,
        "tomato": 25000,
        "onion": 20000,
    }
    
    price = prices.get(crop.lower(), 15000)
    revenue = yield_est * price
    
    # Input costs (₹/ha) - simplified
    costs = {
        "wheat": 40000,
        "rice": 50000,
        "maize": 45000,
        "cotton": 60000,
        "sugarcane": 80000,
        "potato": 120000,
        "tomato": 150000,
        "onion": 100000,
    }
    
    cost = costs.get(crop.lower(), 50000)
    profit = revenue - cost
    
    return round(profit, 2)


def calculate_sustainability(crop: str, request: PredictionRequest) -> float:
    """Calculate sustainability score (0-1)"""
    score = 0.5  # Base score
    
    # Water efficiency
    water_efficient = ["wheat", "maize", "cotton"]
    if crop.lower() in water_efficient:
        score += 0.2
    
    # Crop rotation
    if request.last_crop and request.last_crop.lower() != crop.lower():
        score += 0.15
    
    # Soil health
    if request.soil_ph and 6.0 <= request.soil_ph <= 7.5:
        score += 0.15
    
    return min(score, 1.0)


def generate_explanation(crop: str, request: PredictionRequest, score: float) -> List[str]:
    """Generate explanation for recommendation"""
    explanations = []
    
    if request.soil_ph:
        if 6.0 <= request.soil_ph <= 7.5:
            explanations.append(f"Optimal soil pH ({request.soil_ph:.1f}) for {crop}")
        else:
            explanations.append(f"pH adjustment may be needed for {crop}")
    
    if request.irrigation_available:
        explanations.append("Irrigation availability supports good yield")
    
    if request.soil_n and request.soil_n > 50:
        explanations.append("Adequate nitrogen levels detected")
    
    explanations.append(f"High suitability score: {score:.1%}")
    
    return explanations


def get_rule_based_recommendations(request: PredictionRequest) -> Dict:
    """Fallback rule-based recommendations"""
    crops = ["wheat", "rice", "maize", "cotton", "potato"]
    
    recommendations = []
    for crop in crops[:3]:
        yield_est = estimate_yield(crop, request)
        profit_est = estimate_profit(crop, yield_est)
        sustainability = calculate_sustainability(crop, request)
        explanation = generate_explanation(crop, request, 0.7)
        
        recommendations.append({
            "crop": crop,
            "suitability_score": 0.7,
            "expected_yield": yield_est,
            "expected_profit": profit_est,
            "sustainability_score": sustainability,
            "explanation": explanation
        })
    
    return {"recommendations": recommendations}


@app.post("/diagnose")
async def diagnose_disease(image: UploadFile = File(...)):
    """
    Diagnose crop disease from image
    """
    try:
        # Read image
        from PIL import Image
        import io
        
        image_bytes = await image.read()
        img = Image.open(io.BytesIO(image_bytes))
        img = img.convert("RGB").resize((224, 224))

        if disease_model:
            # TODO: add real preprocessing to match your model's expected input
            # Example placeholder: flatten image and predict
            arr = np.array(img).astype("float32") / 255.0
            arr = np.expand_dims(arr, axis=0)
            try:
                pred = disease_model.predict(arr)
                # You need to map pred -> disease/confidence/treatment for your model
                # Placeholder mapping:
                return {
                    "disease": str(pred),
                    "confidence": 0.75,
                    "treatment": "Consult agronomist for specific treatment plan."
                }
            except Exception as model_err:
                print(f"Disease model inference failed: {model_err}. Falling back to rule-based diagnosis.")

        # Rule-based fallback using simple color heuristics
        diagnosis = diagnose_rule_based(img)
        return diagnosis

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing image: {str(e)}")


def diagnose_rule_based(img: "Image.Image") -> Dict[str, Any]:
    """
    Lightweight heuristic diagnosis for demo purposes.
    Looks at color statistics to guess common issues.
    """
    arr = np.array(img).astype(np.float32)
    mean_channels = arr.reshape(-1, 3).mean(axis=0)  # R, G, B
    r, g, b = mean_channels

    # Ratios to detect discoloration
    yellowish = (r + g) / 2 > b * 1.2
    brownish = r > g * 1.1 and r > b * 1.1
    pale = (r + g + b) / 3 < 80

    if yellowish:
        return {
            "disease": "Nitrogen Deficiency (heuristic)",
            "confidence": 0.65,
            "treatment": "Apply balanced fertilizer rich in nitrogen; monitor leaf recovery.",
        }
    if brownish:
        return {
            "disease": "Leaf Blight (heuristic)",
            "confidence": 0.6,
            "treatment": "Remove affected leaves and apply copper-based fungicide.",
        }
    if pale:
        return {
            "disease": "Possible Chlorosis (heuristic)",
            "confidence": 0.55,
            "treatment": "Check soil pH and iron levels; consider foliar iron spray.",
        }

    return {
        "disease": "Healthy (heuristic)",
        "confidence": 0.8,
        "treatment": "No treatment needed. Continue monitoring.",
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

