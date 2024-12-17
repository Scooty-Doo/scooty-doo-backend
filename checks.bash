#!/bin/bash
ruff format
ruff check --fix
pylint --rcfile=.pylintrc ./api
pylint --rcfile=.pylintrc  ./database
pytest -q 
