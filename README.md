# Getting Started

## API Server
```sh
cd api

# .env setup
echo "JWT_SECRET_KEY=$(openssl rand -base64 32)" >> .env
echo "JWT_ALGO=HS256" >> .env

# libraries setup
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# for local dev
uvicorn main:app --host 0.0.0.0 --port 8080
```

## WebSocket Server
```sh
cd ws
npm install
npm run dev     # for local dev
```

# Architecture
Comming Soon...

# Interface Overview

## APIs
There are two ways to view the API spec:

### 1. FastAPI built-in Swagger
```sh
# Start server first
uvicorn main:app --host 0.0.0.0 --port 8080

open "http://localhost:8080/docs"       #MacOS
xdg-open "http://localhost:8080/docs"   #Linux
start "http://localhost:8080/docs"      #PowerShell
```

### 2. Swagger Editor
1. Open link: https://editor.swagger.io/
2. Import the `openapi.json` provided in the repo
    1. `File` -> `Import File`

## WebSocket

Comming Soon...

