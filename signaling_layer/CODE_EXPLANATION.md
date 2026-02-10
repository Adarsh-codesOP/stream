# Signaling Layer - Code Explanation

This directory contains the **Signaling Layer** of the StreamLink application. It is responsible for real-time communication using WebSockets. It handles the handshake between users for WebRTC (video/audio) and relays chat messages instantly. It is designed to be stateless and scalable using Redis.

## File Breakdown

### 1. `main.py`
**Purpose:** The entry point of the WebSocket server.
- **Functions:**
    - `websocket_endpoint(websocket, room_id, user_id)`: The core loop for handling a user's connection.
        - **Logic Flow:**
            1. Accepts the WebSocket connection.
            2. Validates if the user can join via `grpc_client.validate_join`.
            3. Connects the user to the `ConnectionManager`.
            4. Subscribes to the room's Redis channel.
            5. Notifies others that a new user joined.
            6. Enters a loop to receive messages (`chat`, `offer`, `answer`, `candidate`).
            7. Publishes received messages to Redis (so all instances see them).
            8. Persists chat messages via `grpc_client.store_message`.
    - `handle_redis_message(channel, data)`: A callback triggered when Redis receives a message. It broadcasts the message to all local users in the relevant room.
    - `lifespan(app)`: Manages startup and shutdown events (connecting to Redis).

### 2. `connection_manager.py`
**Purpose:** Manages the active WebSocket connections *in memory* for this specific server instance.
- **Class `ConnectionManager`:**
    - `connect(websocket, room_id, user_id)`: Stores the socket and maps it to the user and room.
    - `disconnect(websocket)`: Removes the socket and cleans up maps.
    - `broadcast_to_room(room_id, message)`: Sends a text message to all sockets currently connected to a specific room on this server.
    - `get_active_users(room_id)`: Returns a list of user IDs currently in a room.
    - `kick_user(room_id, user_id)`: Forcefully closes a user's connection (used for bans).

### 3. `redis_manager.py`
**Purpose:** Handles Pub/Sub messaging via Redis. This allows the system to scale; if we have multiple Signaling Servers, they talk to each other through Redis.
- **Class `RedisManager`:**
    - `subscribe(room_id)`: Listens for messages on a channel named `room:{id}`.
    - `publish(room_id, message)`: Pushes a message to the `room:{id}` channel.
    - `_listener_loop()`: A background task that constantly watches Redis for new messages and triggers the callback in `main.py`.

### 4. `grpc_client.py`
**Purpose:** Acts as a client to the Management Layer's gRPC service.
- **Class `GrpcClient`:**
    - `validate_join(user_id, room_id)`: Asks Management Layer if a user is allowed in a room.
    - `user_joined` / `user_left`: Updates participant counts in the Management Layer.
    - `store_message(...)`: Sends chat messages to the Management Layer for database storage.

### 5. `config.py`
**Purpose:** Reads environment variables to configure host, ports, and connection URLs (Redis, Management Layer).

### Connections
- **Client -> Signaling Layer**: Connects via WebSocket (ws://localhost:8001).
- **Signaling Layer -> Redis**: Publishes and Subscribes to room channels.
- **Signaling Layer -> Management Layer**: Calls gRPC methods (port 50051) for validation and storage.
