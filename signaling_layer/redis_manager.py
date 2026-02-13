import redis.asyncio as redis
import config
import asyncio
import json

class RedisManager:
    def __init__(self):
        self.redis = redis.from_url(config.REDIS_URL, encoding="utf-8", decode_responses=True)
        self.pubsub = self.redis.pubsub()
        self.broadcast_callback = None
        self.is_listening = False
        self.subscribed_rooms = set()

    async def connect(self):
        """Connects and starts the listener loop."""
        if not self.is_listening:
            self.is_listening = True
            asyncio.create_task(self._listener_loop())

    async def _listener_loop(self):
        """Internal loop to consume messages."""
        async with self.pubsub as pb:
           
            await pb.subscribe("global_control")
            
            while True:
                try:
                    message = await pb.get_message(ignore_subscribe_messages=True, timeout=1.0)
                    if message and message['type'] == 'message':
                        if self.broadcast_callback:
                            await self.broadcast_callback(message['channel'], message['data'])
                except Exception as e:
                    print(f"Redis Loop Error: {e}")
                    await asyncio.sleep(1)

    async def set_callback(self, callback):
        self.broadcast_callback = callback

    async def publish(self, room_id: int, message: dict):
        channel = f"room:{room_id}"
        await self.redis.publish(channel, json.dumps(message))

    async def subscribe(self, room_id: int):
        if room_id in self.subscribed_rooms:
            return
        
        channel = f"room:{room_id}"
        print(f"Subscribing to Redis channel: {channel}")
        await self.pubsub.subscribe(channel)
        self.subscribed_rooms.add(room_id)

    async def unsubscribe(self, room_id: int):
        if room_id in self.subscribed_rooms:
            channel = f"room:{room_id}"
            print(f"Unsubscribing from Redis channel: {channel}")
            await self.pubsub.unsubscribe(channel)
            self.subscribed_rooms.remove(room_id)


redis_manager = RedisManager()
