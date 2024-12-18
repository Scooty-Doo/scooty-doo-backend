# scooty-doo-backend
Backend for the Scooty Doo web application

## Development Setup

### Prerequisites
- Python 3.11+
- Docker and Docker Compose
- pip

### Setup Virtual Environment
```bash
# Create virtual environment (from project root)
python3 -m venv .venv

# Activate virtual environment (from project root)
source .venv/bin/activate   # Linux/MacOS

# Install dependencies (from project root)
pip install -r requirements.txt
```

### Setup Database
```bash
# Start PostgreSQL and pgAdmin containers. First go to /database
cd database
docker-compose up
#If this doesn't work you probably haven't started docker service. Start it and try again.

# Create database tables (from project root)
python3 -m api.db.table_creation

# Load mock data
python3 -m database.load_mock_data

```

### Start the API server
```bash
# Start the API server (from project root)
uvicorn api.main:app --reload

# Alternatively set python PATH and run via this:
PYTHONPATH=. fastapi dev api/main.py
```

### Run tests
```bash
# Run without coverage
pytest
# Run with coverage
coverage run -m pytest
# To create reports
coverage report # CLI
coverage html # HTML
```