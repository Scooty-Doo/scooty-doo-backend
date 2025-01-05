FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt requirements.txt

RUN pip install --no-cache-dir --upgrade -r requirements.txt

#This will be amended later, to minimize image
COPY ./api ./api

CMD ["uvicorn", "api.main:app"]

# If running behind a proxy like Nginx or Traefik add --proxy-headers
# CMD ["fastapi", "run", "app/main.py", "--port", "80", "--proxy-headers"]
