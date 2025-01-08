#!/bin/bash
echo Creating tables
python3 -m api.db.table_creation
echo Loading data
python3 -m database.load_mock_data
