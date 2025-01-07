#!/bin/bash
echo Creating tables
python3 -m api.db.table_creation
echo Loading data
python3 -m database.load_mock_data
echo Removing csv data
rm -r ./database
echo Starting API
uvicorn api.main:app --host 0.0.0.0 --port 8000
