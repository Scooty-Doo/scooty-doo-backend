# API for Scooty Doo
This API is made according to REST API principles.
The API is written in Python using FastAPI, and can be run by either building and running from the dockerfile in this folder, or by running the "api" service with 
```
docker compose up api
```
in the parent folder.

The basis of this API was written by following this: [FastAPI Tutorial](https://fastapi.tiangolo.com/tutorial/)

This API is developed in a virtual environment. To replicate it do this (Linux/macOs):
```
# in the api folder
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```
The requirements are listed in the [requirements.txt](requirements.txt) file.

To deactivate the virtual environment, use this terminal command:

```
deactivate
```

To run the server use this command:
```
fastapi dev main.py
```
Use the --port flag to specify port.
