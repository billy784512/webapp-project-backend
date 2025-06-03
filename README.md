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
npm run start   # for production
```

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

### Connection

* **Endpoint**: `ws://localhost:3000`
* **Path**: default (`/socket.io`)
* **Transport**: `websocket`

### Events

1. `enter-room`

   * **Client → Server**
   * Join a specified room

   ```json
    {
        "room_id": "room-123"
    }
   ```

2. `prepare`

   * **Client → Server**
   * Declare that the user is ready

   ```json
    {
        "room_id": "room-123",
        "user_id": "user-a"
    }
   ```

3. `prepare-update`

   * **Server → Room**
   * Broadcast that a user is ready

   ```json
    {
        "sender": "<socket.id>",
        "message": {
            "user_id": "user-a",
            "prepared": true
        }
    }
   ```

4. `check-prepare`

   * **Client → Server**
   * Check if all users in the room are ready

   ```json
    {
        "room_id": "room-123"
    }
   ```

5. `all-prepared`

   * **Server → Room**
   * All users in the room are ready

   ```json
    {
        "room_id": "room-123"
    }
   ```

6. `stroke`

   * **Client → Server**
   * Send stroke drawing data

   ```json
    {
        "room_id": "room-123",
        "user_id": "user-a",
        "color": "#ff0000",
        "path": [[120, 130, 1686000000000], [121, 131, 1686000000500]],
        "brushSize": 3,
        "isEraser": false,
        "operationTimestamp": 1686000000000,
        "operationType": "draw"
    }
   ```

7. `receive-stroke`

   * **Server → Room**
   * Broadcast stroke data to other users in the room

   ```json
    {
        "sender": "<socket.id>",
        "message": { ...stroke payload... }
    }
   ```

8. `submit`

   * **Client → Server**
   * Submit final drawing (base64-encoded)

   ```json
    {
        "room_id": "room-123",
        "user_id": "user-a",
        "base64_str": "<base64-encoded-image>"
    }
   ```

9. `submit-result`

   * **Server → Room**
   * Return scores and winner

   ```json
    {
        "winner": "user-a",
        "scores": {
            "user-a": 85,
            "user-b": 70
        }
    }
   ```

10. `submit-error`

    * **Server → Room**
    * Error occurred during image comparison

    ```json
    {
        "message": "Failed to compare submissions."
    }
    ```

11. `opponent-disconnected`

    * **Server → Opponent**
    * Notify when the opponent disconnects

    ```json
    {
        "room_id": "room-123"
    }
    ```

### Disconnect

* `disconnecting`: Cleanup room and notify opponent
* `disconnect`: Log user disconnecting

