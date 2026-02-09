import grpc
import service_pb2
import service_pb2_grpc
import config

class GrpcClient:
    def __init__(self):
        target = f"{config.MANAGEMENT_SERVICE_HOST}:{config.MANAGEMENT_SERVICE_PORT}"
        self.channel = grpc.insecure_channel(target)
        self.stub = service_pb2_grpc.ManagementServiceStub(self.channel)
        print(f"gRPC Client connected to {target}")

    async def validate_join(self, user_id: int, room_id: int):
        try:
            # gRPC is synchronous by default, but for high-concurrency signaling we might want async
            # For simplicity in this demo, we run it directly. 
            # In production, run in threadpool or use grpc-asyncio.
            response = self.stub.ValidateJoin(service_pb2.JoinRequest(user_id=user_id, room_id=room_id))
            return response.allowed, response.reason
        except grpc.RpcError as e:
            print(f"gRPC Validation Failed: {e}")
            return False, "Internal Error"

    async def user_joined(self, user_id: int, room_id: int):
        try:
            self.stub.UserJoined(service_pb2.JoinRequest(user_id=user_id, room_id=room_id))
        except grpc.RpcError as e:
            print(f"gRPC UserJoined Failed: {e}")

    async def user_left(self, user_id: int, room_id: int):
        try:
            self.stub.UserLeft(service_pb2.JoinRequest(user_id=user_id, room_id=room_id))
        except grpc.RpcError as e:
            print(f"gRPC UserLeft Failed: {e}")

    async def store_message(self, user_id: int, room_id: int, content: str):
        try:
            self.stub.StoreMessage(service_pb2.MessageRequest(user_id=user_id, room_id=room_id, content=content))
        except grpc.RpcError as e:
            print(f"gRPC StoreMessage Failed: {e}")

# Singleton instance
grpc_client = GrpcClient()
