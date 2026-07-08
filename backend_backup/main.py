"""
Kisan Alert AI — FastAPI Application Entry Point

Replaces the Streamlit UI layer (app.py) with a REST API.
All existing modules (weather, crop_rec, disease, irrigation) remain UNCHANGED.
"""

import os
import sys
from pathlib import Path
from contextlib import asynccontextmanager

import pandas as pd
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# ── Ensure project root is on sys.path so `modules` is importable ──
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

load_dotenv(PROJECT_ROOT / ".env")

# ─────────────────────────────────────────────────────────────
# Shared application state (loaded once at startup)
# ─────────────────────────────────────────────────────────────
app_state: dict = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load CSV data once on startup — replaces @st.cache_data."""
    data_dir = PROJECT_ROOT / "data"
    soil_df = pd.read_csv(data_dir / "soil_npk.csv")
    dist_df = pd.read_csv(data_dir / "districts.csv")

    app_state["soil_df"] = soil_df
    app_state["dist_df"] = dist_df
    app_state["states"] = sorted(soil_df["state"].unique().tolist())

    print(f"[OK] Loaded {len(soil_df)} soil rows, {len(dist_df)} district rows")
    yield
    app_state.clear()


# ─────────────────────────────────────────────────────────────
# FastAPI App
# ─────────────────────────────────────────────────────────────
app = FastAPI(
    title="Kisan Alert AI",
    description="Smart crop advisory powered by satellite data & AI",
    version="2.0.0",
    lifespan=lifespan,
)

# CORS — allow everything during development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─────────────────────────────────────────────────────────────
# Register API routers
# ─────────────────────────────────────────────────────────────
from backend.routers import auth, crop, disease, irrigation, weather, dashboard  # noqa: E402

app.include_router(auth.router, prefix="/api/auth", tags=["Auth"])
app.include_router(crop.router, prefix="/api/crop", tags=["Crop"])
app.include_router(disease.router, prefix="/api/disease", tags=["Disease"])
app.include_router(irrigation.router, prefix="/api/irrigation", tags=["Irrigation"])
app.include_router(weather.router, prefix="/api/weather", tags=["Weather"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["Dashboard"])

# ─────────────────────────────────────────────────────────────
# Serve frontend static assets (images, css, js inside frontend/)
# ─────────────────────────────────────────────────────────────
FRONTEND_DIR = PROJECT_ROOT / "frontend"
app.mount("/static/frontend", StaticFiles(directory=str(FRONTEND_DIR)), name="frontend_static")

# ─────────────────────────────────────────────────────────────
# HTML Page Routes — FastAPI serves the frontend directly
# ─────────────────────────────────────────────────────────────

@app.get("/", response_class=HTMLResponse)
async def page_auth_landing():
    """Auth Landing Page — entry point of the application."""
    html_path = FRONTEND_DIR / "kisan_alert_ai_auth_landing" / "code.html"
    return HTMLResponse(content=html_path.read_text(encoding="utf-8"))


@app.get("/location-setup", response_class=HTMLResponse)
async def page_location_setup():
    """Location Setup Page — user selects state, district."""
    html_path = FRONTEND_DIR / "kisan_alert_ai_location_setup" / "code.html"
    return HTMLResponse(content=html_path.read_text(encoding="utf-8"))


@app.get("/dashboard", response_class=HTMLResponse)
async def page_main_dashboard():
    """Primary User Dashboard — permanent dashboard after setup."""
    html_path = FRONTEND_DIR / "kisan_alert_ai_main_dashboard" / "code.html"
    return HTMLResponse(content=html_path.read_text(encoding="utf-8"))


@app.get("/dashboard-admin", response_class=HTMLResponse)
async def page_admin_dashboard():
    """Secondary / Admin Dashboard — optional alternative view."""
    html_path = FRONTEND_DIR / "kisan_alert_ai_dashboard" / "code.html"
    return HTMLResponse(content=html_path.read_text(encoding="utf-8"))


@app.get("/disease-detection", response_class=HTMLResponse)
async def page_disease_detection():
    """Disease Detection Page — upload crop image for diagnosis."""
    html_path = FRONTEND_DIR / "kisan_alert_ai_disease_detection" / "code.html"
    return HTMLResponse(content=html_path.read_text(encoding="utf-8"))


@app.get("/weather", response_class=HTMLResponse)
async def page_weather():
    """Weather Intelligence Center."""
    html_path = FRONTEND_DIR / "kisan_alert_ai_weather_intelligence_center" / "code.html"
    return HTMLResponse(content=html_path.read_text(encoding="utf-8"))


@app.get("/profile", response_class=HTMLResponse)
async def page_profile():
    """Farmer Profile Page."""
    html_path = FRONTEND_DIR / "kisan_alert_ai_farmer_profile" / "code.html"
    return HTMLResponse(content=html_path.read_text(encoding="utf-8"))


# ─────────────────────────────────────────────────────────────
# Health check
# ─────────────────────────────────────────────────────────────
@app.get("/api/health")
async def health_check():
    return {
        "status": "ok",
        "states_loaded": len(app_state.get("states", [])),
        "soil_rows": len(app_state.get("soil_df", [])),
    }
