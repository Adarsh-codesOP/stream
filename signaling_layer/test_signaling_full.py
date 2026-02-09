import asyncio
import websockets
import json
import grpc
import service_pb2
import service_pb2_grpc
import random

# Configuration
SIGNALING_URL = "ws://localhost:8001/ws"
MANAGEMENT_GRPC = "localhost:50051"

async def setup_test_data():
    """
    Helpers to create a User and Room in the Management Layer 
    so validation passes when we connect to Signaling.
    """
    print("[Setup] Connecting to Management Layer to seed data...")
    channel = grpc.insecure_channel(MANAGEMENT_GRPC)
    stub = service_pb2_grpc.ManagementServiceStub(channel)

    # 1. Register User A
    suffix = random.randint(1000, 9999)
    user_a = f"alice_{suffix}"
    resp_a = stub.Register(service_pb2.RegisterRequest(username=user_a, password="password"))
    uid_a = resp_a.user_id if resp_a.user_id != -1 else 1
    print(f"[Setup] User A: {user_a} (ID: {uid_a})")

    # 2. Register User B
    user_b = f"bob_{suffix}"
    resp_b = stub.Register(service_pb2.RegisterRequest(username=user_b, password="password"))
    uid_b = resp_b.user_id if resp_b.user_id != -1 else 2
    print(f"[Setup] User B: {user_b} (ID: {uid_b})")

    # 3. Create Room
    room_name = f"ChatRoom_{suffix}"
    resp_room = stub.CreateRoom(service_pb2.CreateRoomRequest(name=room_name, max_participants=10, creator_id=uid_a))
    room_id = resp_room.id
    print(f"[Setup] Room: {room_name} (ID: {room_id})")

    return uid_a, uid_b, room_id

async def connect_and_listen(name, user_id, room_id, send_messages=None):
    """
    Simulates a client connecting to the signaling server.
    """
    uri = f"{SIGNALING_URL}/{room_id}/{user_id}"
    print(f"[{name}] Connecting to {uri}...")
    
    try:
        async with websockets.connect(uri) as websocket:
            print(f"[{name}] Connected!")

            # Send messages if any
            if send_messages:
                for msg in send_messages:
                    payload = {
                        "type": "chat",
                        "content": msg
                    }
                    await websocket.send(json.dumps(payload))
                    print(f"[{name}] Sent: {msg}")
                    await asyncio.sleep(0.5)

            # Listen for incoming
            # We listen for a few seconds to catch echoes
            try:
                while True:
                    response = await asyncio.wait_for(websocket.recv(), timeout=3.0)
                    data = json.loads(response)
                    print(f"[{name}] Received: {data}")
            except asyncio.TimeoutError:
                print(f"[{name}] No more messages (Timeout)")
            
    except Exception as e:
        print(f"[{name}] Error: {e}")

async def main():
    # 1. Setup Data
    try:
        uid_a, uid_b, room_id = await setup_test_data()
    except Exception as e:
        print(f"Setup Failed: {e}")
        print("Ensure Management Server is running on port 50051")
        return

    print("\n--- Starting Signaling Test ---\n")

    # 2. Run two clients concurrently
    # Alice sends messages, Bob just listens (and receives)
    
    task_a = asyncio.create_task(connect_and_listen("Alice", uid_a, room_id, send_messages=["Hello Bob!", "How are you?"]))
    task_b = asyncio.create_task(connect_and_listen("Bob", uid_b, room_id, send_messages=[]))

    await asyncio.gather(task_a, task_b)
    print("\n--- Test Complete ---")

if __name__ == "__main__":
    asyncio.run(main())
