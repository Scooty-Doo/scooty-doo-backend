#!/bin/bash
COLOR='\033[0;32m'
NC='\033[0m' # no color
printf "\n${COLOR} Formatting with ruff ${NC}\n"
echo _______________________
ruff format
printf "\n${COLOR} Checking with ruff ${NC}\n"
echo _______________________
ruff check --fix
printf "\n${COLOR} Linting api with pylint${NC}\n"
echo _______________________
pylint --fail-under=9 ./api
printf "\n${COLOR}Linting database with pylint${NC}\n"
echo _______________________
pylint --fail-under=9 ./database
printf "\n${COLOR}Linting tests with pylint${NC}\n"
echo _______________________
pylint --fail-under=9 ./tests
printf "\n${COLOR}Running tests with pytest${NC}\n"
echo _______________________
coverage run -m pytest -q
printf "\n${COLOR}Generating coverage${NC}\n"
echo _______________________
coverage html
coverage report
