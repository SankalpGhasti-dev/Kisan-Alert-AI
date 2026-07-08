FROM python:3.11-slim

WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Expose port 8080 for Google Cloud Run
EXPOSE 8080

# Run the FastAPI application (replaces Streamlit)
# Legacy app.py is kept as backup — do not delete until migration verified
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8080"]
