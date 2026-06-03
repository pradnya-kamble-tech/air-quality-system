🌍 Air Quality Monitor & Prediction System

Real-time air quality monitoring and prediction system focused on **India**.

## Quick Start

```bash
cd backend

# Create & activate virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1      # Windows PowerShell

# Install dependencies
pip install -r requirements.txt

# Run the development server
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```


## API Endpoints

| Method | Path      | Description                      |
|--------|-----------|----------------------------------|
| GET    | `/`       | Root — confirms API is running   |
| GET    | `/health` | Health check with region info    |
| GET    | `/docs`   | Swagger UI (auto-generated)      |
| GET    | `/redoc`  | ReDoc (auto-generated)           |



## Running Tests

```bash
cd backend
pytest tests/ -v
```

## Project Structure

```
air-quality-system/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app entry point
│   │   ├── core/config.py       # Settings from .env
│   │   └── api/routes/health.py # Health endpoint
│   ├── tests/test_health.py     # Endpoint tests
│   ├── requirements.txt
│   └── .env
└── README.md
```
