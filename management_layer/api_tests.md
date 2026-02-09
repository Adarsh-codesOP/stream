# StreamLink Management Layer - API Testing Guide

Base URL: `http://localhost:8000`

## 1. Register a User
**URL:** `POST /auth/register`
**Description:** Creates a new user account.

**Request:**
```bash
curl -X 'POST' \
  'http://localhost:8000/auth/register' \
  -H 'Content-Type: application/json' \
  -d '{
  "username": "alice",
  "password": "secretpassword"
}'
```

**Expected Output:**
```json
{
  "username": "alice",
  "id": 1,
  "is_banned": false
}
```

---

## 2. Login
**URL:** `POST /auth/login`
**Description:** Authenticates a user and returns a Bearer token.

**Request:**
```bash
curl -X 'POST' \
  'http://localhost:8000/auth/login' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  -d 'grant_type=password&username=alice&password=secretpassword'
```

**Expected Output:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI...", 
  "token_type": "bearer"
}
```
*(Save this token for subsequent requests! We will refer to it as `$TOKEN`)*

---

## 3. Create a Room
**URL:** `POST /rooms/`
**Description:** Creates a new video conference room.

**Request:**
```bash
curl -X 'POST' \
  'http://localhost:8000/rooms/' \
  -H 'Authorization: Bearer $TOKEN' \
  -H 'Content-Type: application/json' \
  -d '{
  "name": "General",
  "max_participants": 10
}'
```

**Expected Output:**
```json
{
  "name": "General",
  "max_participants": 10,
  "id": 1,
  "is_active": true,
  "created_by": 1
}
```

---

## 4. List Rooms
**URL:** `GET /rooms/`
**Description:** Lists all available rooms.

**Request:**
```bash
curl -X 'GET' \
  'http://localhost:8000/rooms/' \
  -H 'accept: application/json'
```

**Expected Output:**
```json
[
  {
    "name": "General",
    "max_participants": 10,
    "id": 1,
    "is_active": true,
    "created_by": 1
  }
]
```

---

## 5. Block a User from a Room (HTTP)
**URL:** `POST /rooms/{room_id}/block`
**Description:** Bans a user from a specific room. Only the room creator can do this.
*(Assume we want to ban User ID 2 from Room ID 1)*

**Request:**
```bash
curl -X 'POST' \
  'http://localhost:8000/rooms/1/block' \
  -H 'Authorization: Bearer $TOKEN' \
  -H 'Content-Type: application/json' \
  -d '{
  "user_id": 2,
  "reason": "Spamming"
}'
```

**Expected Output:**
```json
{
  "message": "User banned from room"
}
```

---

## 6. Fetch Messages
**URL:** `GET /rooms/{room_id}/messages`
**Description:** Retrieves chat history for a room.

**Request:**
```bash
curl -X 'GET' \
  'http://localhost:8000/rooms/1/messages' \
  -H 'Authorization: Bearer $TOKEN' \
  -H 'accept: application/json'
```

**Expected Output:**
*(Empty list initially, as messages are added via gRPC from the Signaling Server)*
```json
[]
```

---

## 7. Global System Ban (Admin)
**URL:** `POST /users/ban`
**Description:** Globally bans a user from the entire system.

**Request:**
```bash
curl -X 'POST' \
  'http://localhost:8000/users/ban' \
  -H 'Authorization: Bearer $TOKEN' \
  -H 'Content-Type: application/json' \
  -d '{
  "user_id": 2
}'
```

**Expected Output:**
```json
{
  "message": "User bob has been globally banned"
}
```

---

## 8. Unban a User (Admin)
**URL:** `POST /users/unban`
**Description:** Removes the global ban from a user.

**Request:**
```bash
curl -X 'POST' \
  'http://localhost:8000/users/unban' \
  -H 'Authorization: Bearer $TOKEN' \
  -H 'Content-Type: application/json' \
  -d '{
  "user_id": 1
}'
```

**Expected Output:**
```json
{
  "message": "User alice has been unbanned"
}
```
