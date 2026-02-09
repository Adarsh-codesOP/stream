import asyncio
import websockets
import json
import requests
import time

# Metrics
API_URL = "http://127.0.0.1:8000"
WS_URL = "ws://127.0.0.1:8001"

async def test_chat_persistence():
    print("--- Starting Chat Persistence Test ---")

    # 1. Create a Room
    print("[1] Creating Room...")
    room_name = f"TestRoom_{int(time.time())}"
    
    username = f"testuser_{int(time.time())}"
    password = "password123"
    
    # Register
    print(f"Registering user at {API_URL}/auth/register")
    try:
        reg_res = requests.post(f"{API_URL}/auth/register", json={"username": username, "password": password})
        print(f"Register Response: {reg_res.status_code} {reg_res.text}")
    except Exception as e:
        print(f"Error registering: {e}")

    # Login
    print(f"Logging in at {API_URL}/auth/login")
    auth_res = requests.post(f"{API_URL}/auth/login", data={"username": username, "password": password})
    print(f"Login Response: {auth_res.status_code} {auth_res.text}")
    
    if auth_res.status_code != 200:
        return
    
    token = auth_res.json()["access_token"]
    user_id = auth_res.json()["user_id"]
    headers = {"Authorization": f"Bearer {token}"}

    # Create Room
    print(f"Creating room at {API_URL}/rooms")
    # Try without trailing slash first
    room_url = f"{API_URL}/rooms"
    room_res = requests.post(room_url, json={"name": room_name, "max_participants": 5}, headers=headers)
    
    if room_res.status_code == 307: # Redirect
        print("Redirected, trying with slash...")
        room_url = f"{API_URL}/rooms/"
        room_res = requests.post(room_url, json={"name": room_name, "max_participants": 5}, headers=headers)

    print(f"Create Room Response: {room_res.status_code} {room_res.text}")
    
    if room_res.status_code != 200:
        return
    
    room_id = room_res.json()["id"]
    print(f"Room '{room_name}' (ID: {room_id}) created.")

    # 2. Connect via WebSocket and Send Message
    print(f"[2] Connecting to WebSocket as User {user_id}...")
    uri = f"{WS_URL}/ws/{room_id}/{user_id}"
    
    async with websockets.connect(uri) as websocket:
        # Wait for handshake/existing users
        await websocket.recv() 
        
        test_message = f"Hello Persistence {int(time.time())}"
        print(f"[3] Sending Message: '{test_message}'")
        
        await websocket.send(json.dumps({
            "type": "chat",
            "content": test_message
        }))
        
        # Wait a bit for async processing
        await asyncio.sleep(2)

    # 3. Query Database via API
    print("[4] Querying API for Chat History...")
    history_res = requests.get(f"{API_URL}/rooms/{room_id}/messages")
    print(f"History Response: {history_res.status_code}")
    
    if history_res.status_code == 200:
        messages = history_res.json()
        found = False
        for msg in messages:
            if msg["content"] == test_message and msg["user_id"] == user_id:
                found = True
                print("SUCCESS: Message found in database history!")
                print(f"Stored Message: {msg}")
                break
        
        if not found:
            print("FAILURE: Message NOT found in history.")
            print(f"Retrieved History: {messages}")
    else:
        print(f"FAILURE: API Query Failed: {history_res.status_code} {history_res.text}")

if __name__ == "__main__":
    # Check API health
    try:
        r = requests.get(f"{API_URL}/openapi.json")
        print(f"API Health Check: {r.status_code}")
    except Exception as e:
        print(f"API Health Check Failed: {e}")
        exit(1)
        
    asyncio.run(test_chat_persistence())
