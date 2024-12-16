#!/bin/bash
ruff format
ruff check
pylint ./api
pylint ./database
pytest -q 
