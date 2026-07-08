# Kisan Alert AI

Kisan Alert AI is an agriculture-focused web application that combines weather insights, disease detection, location-based setup, and a farmer dashboard in a single project.

The repository contains a Python backend, multiple HTML-based frontend pages, static JavaScript assets, environment configuration, Docker support, and supporting data and module directories.

## Features

- Farmer-friendly multi-page interface with:
  - `index.html`
  - `dashboard.html`
  - `weather.html`
  - `profile.html`
  - `location-setup.html`
  - `disease-detection.html`
  - `copilot.html`
- Python backend powered through `app.py`
- Agriculture-oriented dashboard and weather monitoring workflow
- Crop disease detection module
- Firebase-related configuration support
- Dockerized deployment support
- Environment-based configuration using `.env.example`

## Project Structure

```text
Kisan-Alert-AI/
├── assets/js/
├── backend/
├── backend_backup/
├── data/
├── frontend_backup/
├── modules/
├── templates/
├── .env.example
├── .gitignore
├── Dockerfile
├── app.py
├── audit.py
├── copilot.html
├── dashboard.html
├── disease-detection.html
├── dummy.jpg
├── firebase_config.py
├── generate_accurate_coords.py
├── index.html
├── location-setup.html
├── profile.html
├── requirements.txt
└── weather.html
```

## Tech Stack

- **Frontend:** HTML, JavaScript
- **Backend:** Python
- **Configuration:** `.env`
- **Deployment:** Docker
- **Optional Services:** Firebase integration

## Setup Instructions

### 1. Clone the repository

```bash
git clone https://github.com/SankalpGhasti-dev/Kisan-Alert-AI.git
cd Kisan-Alert-AI
```

### 2. Create a virtual environment

```bash
python -m venv venv
source venv/bin/activate
```

On Windows:

```bash
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

```bash
cp .env.example .env
```

Update the `.env` file with your actual configuration values.

### 5. Run the application

```bash
python app.py
```

## Docker Setup

```bash
docker build -t kisan-alert-ai .
docker run -p 5000:5000 kisan-alert-ai
```

## Main Pages

| Page | Purpose |
|------|---------|
| `index.html` | Landing page |
| `dashboard.html` | Main farmer dashboard |
| `weather.html` | Weather insights for agriculture |
| `location-setup.html` | User or farm location setup |
| `disease-detection.html` | Crop disease detection interface |
| `profile.html` | User profile management |
| `copilot.html` | Assistant or support interface |

## Use Cases

- Monitor agriculture-related weather conditions
- Set up location-aware alerts and recommendations
- Use a dashboard to track important farming insights
- Detect crop disease through a dedicated interface
- Support smarter farmer decision-making with AI-enabled tools

## Development Notes

This repository combines frontend-heavy development with Python backend functionality. It is suitable for agriculture technology demos, student innovation projects, and AI-for-farming solutions.

## Contribution

1. Fork the repository
2. Create a new branch
3. Make your changes
4. Commit and push
5. Open a pull request

## License

No license file is currently specified. Add a license if you want to define usage and contribution permissions clearly.
