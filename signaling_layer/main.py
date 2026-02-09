from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import asyncio
import json
import uvicorn
from contextlib import asynccontextmanager

from connection_manager import manager
from redis_manager import redis_manager
from grpc_client import grpc_client
import config

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("Starting Redis Manager...")
    await redis_manager.set_callback(handle_redis_message)
    await redis_manager.connect()
    yield
    # Shutdown
    print("Shutting down...")

app = FastAPI(lifespan=lifespan)
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


async def handle_redis_message(channel: str, data: str):
    """Callback triggered by RedisManager when a message arrives."""
    if channel.startswith("room:"):
        try:
            room_id = int(channel.split(":")[1])
            message_data = json.loads(data)
            
            # Handle System Kick
            if message_data.get("type") == "system_kick":
                target_user_id = message_data.get("user_id")
                print(f"Received System Kick for User {target_user_id} in Room {room_id}")
                await manager.kick_user(room_id, target_user_id)
                return

            # Broadcast to local users in that room
            await manager.broadcast_to_room(room_id, data)
        except Exception as e:
            print(f"Error handling redis message: {e}")

@app.websocket("/ws/{room_id}/{user_id}")
async def websocket_endpoint(websocket: WebSocket, room_id: int, user_id: int):
    # 2. User Connects (Handshake)
    await websocket.accept()

    try:
        # 4. Ask Management Server: Can Join?
        allowed, reason = await grpc_client.validate_join(user_id, room_id)
        if not allowed:
            print(f"Join Denied for User {user_id}: {reason}")
            await websocket.close(code=1008, reason=reason)
            return

        # 6. Map in Memory
        await manager.connect(websocket, room_id, user_id)
        
        # 7. Redis Subscribe
        await redis_manager.subscribe(room_id)

        # Notify Management (User Joined -> Count++)
        try:
            await grpc_client.user_joined(user_id, room_id)
        except Exception as e:
            print(f"gRPC Join/Update Error: {e}")

        # Send existing users list to the new user
        active_user_ids = manager.get_active_users(room_id)
        await websocket.send_text(json.dumps({
            "type": "existing_users",
            "ids": active_user_ids
        }))

        # Broadcast "user_joined" to room (Triggers WebRTC Offers from others)
        await redis_manager.publish(room_id, {
            "type": "user_joined",
            "user_id": user_id
        })

        # 9. Handle Messages
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            msg_type = message_data.get("type")

            # Simple Chat Message
            if msg_type == "chat":
                content = message_data.get("content")
                
                # A) Real-time delivery (Redis)
                payload = {
                    "type": "chat",
                    "user_id": user_id,
                    "content": content
                }
                await redis_manager.publish(room_id, payload)
                
                # B) Persistence (Management)
                try:
                    asyncio.create_task(grpc_client.store_message(user_id, room_id, content))
                except Exception as e:
                     print(f"gRPC Store Message Error: {e}")

            # WebRTC Signaling (Offer, Answer, ICE Candidates)
            elif msg_type in ["offer", "answer", "candidate"]:
                # Broadcast signal to room (Mesh networking / Peer-to-Peer)
                payload = {
                    "type": msg_type,
                    "user_id": user_id, # Sender
                    "target_id": message_data.get("target_id"), # Intended Recipient (for P2P)
                    "data": message_data.get("data")
                }
                # Optimization: We could send only to target, but for now broadcast is easier
                # Client must filter by 'target_id'
                await redis_manager.publish(room_id, payload)

    except WebSocketDisconnect:
        # 13. User Disconnects
        print(f"User {user_id} disconnected")
        manager.disconnect(websocket)
        
        # Check if room is empty
        if manager.get_room_count(room_id) == 0:
            await redis_manager.unsubscribe(room_id)

        try:
            await grpc_client.user_left(user_id, room_id)
        except Exception as e:
            print(f"gRPC Leave Error: {e}")
            
        # Broadcast "user_left"
        await redis_manager.publish(room_id, {
            "type": "user_left",
            "user_id": user_id
        })

if __name__ == "__main__":
    uvicorn.run("main:app", host=config.HOST, port=config.PORT, reload=True)
