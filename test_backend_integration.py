import asyncio
import redis.asyncio as redis
import grpc
import sys
import os

# Adjust path to include signaling_layer for imports
sys.path.append(os.path.join(os.getcwd(), 'signaling_layer'))

# Import generated protobufs
import service_pb2
import service_pb2_grpc

# Configuration
REDIS_URL = "redis://127.0.0.1:6379"
GRPC_HOST = "127.0.0.1"
GRPC_PORT = 50051

# Force UTF-8 for stdout
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

def log(msg):
    print(msg)


async def test_redis():
    log(f"\n--- Testing Redis Connection to {REDIS_URL} ---")
    try:
        r = redis.from_url(REDIS_URL, encoding="utf-8", decode_responses=True)
        await r.ping()
        log("✅ Redis PING successful.")
        
        # Test PubSub
        pubsub = r.pubsub()
        await pubsub.subscribe("test_channel")
        
        # Ensure subscription is active by waiting for the subscribe message
        # This prevents the race condition where we publish before the sub is registered
        confirmation = await pubsub.get_message(ignore_subscribe_messages=False, timeout=5.0)
        if confirmation and confirmation['type'] == 'subscribe':
             log("✅ Subscribed to 'test_channel' (Confirmed).")
        else:
             log(f"⚠️ Warning: Did not receive subscription confirmation. Got: {confirmation}")

        await r.publish("test_channel", "Hello Redis!")
        log("✅ Published message to 'test_channel'.")
        
        # Wait for message
        message = await pubsub.get_message(ignore_subscribe_messages=True, timeout=5.0)
        if message and message['data'] == "Hello Redis!":
            log(f"✅ Received message: {message['data']}")
        else:
            log(f"❌ Failed to receive message via PubSub. Got: {message}")
            
        await r.aclose()
            
    except Exception as e:
        log(f"❌ Redis Test Failed: {e}")

async def test_grpc():
    log(f"\n--- Testing gRPC Connection to {GRPC_HOST}:{GRPC_PORT} ---")
    try:
        channel = grpc.aio.insecure_channel(f"{GRPC_HOST}:{GRPC_PORT}")
        stub = service_pb2_grpc.ManagementServiceStub(channel)
        
        # Test ValidateJoin (Read-onlyish)
        # Using dummy IDs 1, 1 (assuming they might exist or at least not crash)
        log("Sending ValidateJoin request...")
        response = await stub.ValidateJoin(service_pb2.JoinRequest(user_id=1, room_id=1))
        log(f"✅ ValidateJoin response: Allowed={response.allowed}, Reason='{response.reason}'")
        
        await channel.close()
        
    except grpc.RpcError as e:
        log(f"❌ gRPC Test Failed: {e.code()}: {e.details()}")
    except Exception as e:
        log(f"❌ gRPC Test Error: {e}")

async def main():
    await test_redis()
    await test_grpc()

if __name__ == "__main__":
    asyncio.run(main())
