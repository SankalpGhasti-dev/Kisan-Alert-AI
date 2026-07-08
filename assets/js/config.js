// config.js
// This configuration file points the frontend to the Cloud Run / FastAPI backend URL.
// When testing locally, leave it as localhost:8000.
// Before deploying to production, update this to your Cloud Run URL.

const API_BASE_URL = "https://kisan-alert-ai-production.up.railway.app";
window.API_BASE_URL = API_BASE_URL;
