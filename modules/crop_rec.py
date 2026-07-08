import os
import pandas as pd
import numpy as np
import joblib
from sklearn.ensemble import RandomForestClassifier

MODEL_PATH = os.path.join(os.path.dirname(__file__), "..", "models", "crop_model.pkl")

def get_emoji(crop):
    emojis = {
        'rice': '🌾', 'wheat': '🌾', 'maize': '🌽', 'sugarcane': '🎋',
        'cotton': '☁️', 'soybean': '🌱', 'groundnut': '🥜', 'onion': '🧅',
        'tomato': '🍅', 'potato': '🥔', 'banana': '🍌', 'chickpea': '🌱',
        'apple': '🍎', 'orange': '🍊', 'papaya': '🍈', 'coconut': '🥥',
        'grapes': '🍇', 'watermelon': '🍉', 'mango': '🥭', 'pomegranate': '🌺',
        'lentil': '🌱', 'blackgram': '🌱', 'mungbean': '🌱', 'mothbeans': '🌱',
        'pigeonpeas': '🌱', 'kidneybeans': '🫘', 'muskmelon': '🍈', 'coffee': '☕',
        'jute': '🌾'
    }
    return emojis.get(str(crop).lower(), '🌱')

def train_model():
    url = "https://raw.githubusercontent.com/dsrscientist/dataset1/master/Crop_recommendation.csv"
    df = pd.read_csv(url)
    
    X = df[['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall']]
    y = df['label']
    
    clf = RandomForestClassifier(n_estimators=100, random_state=42, oob_score=True)
    clf.fit(X, y)
    
    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
    joblib.dump(clf, MODEL_PATH)
    return clf, df

def load_or_train_model():
    if os.path.exists(MODEL_PATH):
        try:
            clf = joblib.load(MODEL_PATH)
            return clf
        except Exception:
            pass
    clf, _ = train_model()
    return clf

def predict(N, P, K, ph, temperature, humidity, rainfall):
    clf = load_or_train_model()
    # Order required: 'N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall'
    features = np.array([[N, P, K, temperature, humidity, ph, rainfall]])
    
    probs = clf.predict_proba(features)[0]
    classes = clf.classes_
    
    top_indices = np.argsort(probs)[::-1][:3]
    results = []
    for idx in top_indices:
        crop = classes[idx]
        conf = probs[idx]
        results.append({
            "crop": crop,
            "confidence": float(conf),
            "emoji": get_emoji(crop)
        })
    return results
