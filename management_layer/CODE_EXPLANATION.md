# Management Layer - Code Explanation

This directory contains the **Management Layer** of the StreamLink application. It is responsible for user authentication, room management, and data persistence (users, rooms, messages) using a PostgreSQL database. It exposes both an HTTP API (FastAPI) for the Client and a gRPC service for the Signaling Layer.

## File Breakdown

### 1. `main.py`
**Purpose:** The entry point of the application.
- **Functions:**
    - `run_grpc_server()`: Starts the gRPC server in a separate thread on port `50051`. This allows the Signaling Layer to communicate with this layer.
    - `startup_event()`: An event handler that runs when the FastAPI app starts. It launches the gRPC server thread.
- **Logic:** Initializes the `FastAPI` application, configures CORS (Cross-Origin Resource Sharing) to allow frontend access, includes the routers (`auth` and `rooms`), and starts the server using `uvicorn`.

### 2. `database.py`
**Purpose:** Handles the database connection.
- **Functions:**
    - `get_db()`: A dependency function used in API endpoints to get a database session. It ensures the session is closed after the request is finished.
- **Variables:**
    - `SQLALCHEMY_DATABASE_URL`: The connection string for the PostgreSQL database. It can be configured for Docker or local execution.
    - `engine`: The SQLAlchemy engine that manages database connections.
    - `SessionLocal`: A factory for creating new database sessions.
    - `Base`: The base class for all database models.

### 3. `models.py`
**Purpose:** Defines the database structure (Schema) using SQLAlchemy ORM.
- **Classes:**
    - `User`: Represents a user in the system (id, username, password_hash, is_banned).
    - `Room`: Represents a chat room (id, name, max_participants, is_active, created_by).
    - `Message`: Represents a chat message (id, content, timestamp, room_id, sender_id).
    - `RoomBan`: Represents a user banned from a specific room.
- **Logic:** These classes map directly to tables in the PostgreSQL database.

### 4. `schemas.py`
**Purpose:** Defines the data structures for API requests and responses using Pydantic.
- **Classes (Data Transfer Objects):**
    - `UserCreate` / `UserResponse`: Data required to register a user and the data returned.
    - `RoomCreate` / `RoomResponse`: Data for creating and viewing rooms.
    - `MessageCreate` / `MessageResponse`: Data for sending and viewing messages.
    - `Token`: Structure of the authentication token returned on login.
- **Logic:** Used by FastAPI to validate incoming JSON data and format outgoing JSON responses.

### 5. `auth.py`
**Purpose:** API Router for user authentication.
- **Functions:**
    - `register(user, db)`: Creates a new user in the database. Hashes the password before saving.
    - `login(form_data, db)`: Verifies username and password. If valid, generates and returns a JWT (JSON Web Token) for authentication.
    - `create_access_token(data, expires_delta)`: Utility function to create a signed JWT.
- **Logic:** Handles the security aspect of the system.

### 6. `rooms.py`
**Purpose:** API Router for room operations.
- **Functions:**
    - `create_room(room, current_user, db)`: Creates a new chat room. Ensures the room name is unique.
    - `list_rooms(db)`: Returns a list of all active rooms.
    - `get_room(room_id, db)`: Returns details of a specific room.
    - `block_user_from_room(...)`: Allows a room creator to ban a user from their room. This also sends a "kick" message to Redis to disconnect the user immediately.
    - `get_room_messages(room_id, limit, db)`: Retrieves the chat history for a room.
- **Logic:** Contains the business logic for managing rooms and their interactions.

### 7. `grpc_server.py`
**Purpose:** Implements the gRPC service defined in `service.proto`. This is how the Signaling Layer talks to the Management Layer.
- **Class `ManagementService` Functions:**
    - `Register` / `Login`: Allows authentication via gRPC (unused if Client uses HTTP, but available).
    - `CreateRoom` / `ListRooms`: Allows room management via gRPC.
    - `ValidateJoin(request)`: Checks if a user is allowed to join a room (e.g., checks if they are banned or if the room exists).
    - `UserJoined(request)`: Updates the database when a user joins (increments participant count).
    - `UserLeft(request)`: Updates the database when a user leaves (decrements participant count).
    - `StoreMessage(request)`: Saves a chat message to the database.
- **Logic:** Acts as a backend interface for the Signaling Layer, ensuring validations and data updates happen centrally in the database.

### 8. `requirements.txt`
**Purpose:** Lists all Python libraries required to run this layer (e.g., `fastapi`, `sqlalchemy`, `grpcio`).

### Connections
- **Frontend -> Management Layer**: Connects via HTTP (port 8000) for Login, Registration, and Fetching Room/Message lists.
- **Signaling Layer -> Management Layer**: Connects via gRPC (port 50051) to validate user actions (join, message) and persist data.
