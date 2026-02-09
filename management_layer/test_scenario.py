import grpc
import service_pb2
import service_pb2_grpc
import time
import random

def run_test():
    print("="*60)
    print("      STREAMLINK MANAGEMENT LAYER - COMPREHENSIVE TEST")
    print("="*60)
    
    channel = grpc.insecure_channel('localhost:50051')
    stub = service_pb2_grpc.ManagementServiceStub(channel)

    def print_step(step, msg):
        print(f"\n[Step {step}] {msg}")

    # --- 1. Registration ---
    print_step(1, "Registering 3 Users (Admin, Bob, Charlie)")
    users = {}
    for name in ["admin_user", "bob", "charlie"]:
        suffix = random.randint(1000, 9999) # Avoid duplicate errors
        username = f"{name}_{suffix}"
        res = stub.Register(service_pb2.RegisterRequest(username=username, password="password123"))
        if res.user_id != -1:
            print(f"  + Registered {username} (ID: {res.user_id})")
            users[name] = {"id": res.user_id, "name": username}
        else:
            print(f"  ! Failed to register {username} (Might exist)")
            # Fallback for demo if running repeatedly without db reset
            users[name] = {"id": 1, "name": "fallback"} 

    admin = users["admin_user"]
    bob = users["bob"]
    charlie = users["charlie"]

    # --- 2. Login ---
    print_step(2, "Verifying Login")
    login_res = stub.Login(service_pb2.LoginRequest(username=admin['name'], password="password123"))
    if login_res.access_token:
        print(f"  + Admin Logged in successfully. Token: {login_res.access_token[:20]}...")
    else:
        print("  ! Admin login failed")

    # --- 3. Create Room ---
    print_step(3, f"Admin ({admin['name']}) Creating 'Alpha Room'")
    room_res = stub.CreateRoom(service_pb2.CreateRoomRequest(
        name=f"Alpha_{random.randint(100,999)}", 
        max_participants=5, 
        creator_id=admin['id']
    ))
    room_id = room_res.id
    print(f"  + Room Created: {room_res.name} (ID: {room_id})")

    # --- 4. Users Join ---
    print_step(4, "Bob and Charlie Join the Room")
    
    # Bob Joins
    params = service_pb2.JoinRequest(user_id=bob['id'], room_id=room_id)
    check = stub.ValidateJoin(params)
    if check.allowed:
        stub.UserJoined(params)
        print(f"  + Bob Joined (Allowed: {check.allowed})")
    else:
        print(f"  ! Bob Failed to Join: {check.reason}")

    # Charlie Joins
    params_c = service_pb2.JoinRequest(user_id=charlie['id'], room_id=room_id)
    check_c = stub.ValidateJoin(params_c)
    if check_c.allowed:
        stub.UserJoined(params_c)
        print(f"  + Charlie Joined (Allowed: {check_c.allowed})")

    # Verify Count
    print_step(5, "Verifying Room Participant Count")
    list_res = stub.ListRooms(service_pb2.Empty())
    for r in list_res.rooms:
        if r.id == room_id:
            print(f"  > Room {r.name}: {r.current_participants}/{r.max_participants} participants")

    # --- 6. Chatting ---
    print_step(6, "Exchange Messages")
    msg1 = stub.StoreMessage(service_pb2.MessageRequest(user_id=bob['id'], room_id=room_id, content="Hi everyone!"))
    print(f"  + Bob sent message: Success={msg1.success}")
    
    msg2 = stub.StoreMessage(service_pb2.MessageRequest(user_id=charlie['id'], room_id=room_id, content="Hello Bob!"))
    print(f"  + Charlie sent message: Success={msg2.success}")

    # --- 7. Ban User ---
    print_step(7, "Admin Blocks Bob from the Room (Reason: 'Spam')")
    ban_res = stub.BlockUser(service_pb2.BlockRequest(
        requester_id=admin['id'], # Creator
        room_id=room_id,
        user_to_block_id=bob['id'],
        reason="Spam"
    ))
    print(f"  + Block Result: Success={ban_res.success}, Error='{ban_res.error}'")

    # --- 8. Verify Ban Effects ---
    print_step(8, "Verifying Ban Effects on Bob")
    # Bob tries to chat
    msg3 = stub.StoreMessage(service_pb2.MessageRequest(user_id=bob['id'], room_id=room_id, content="Can you hear me?"))
    print(f"  > Bob tries to chat: Success={msg3.success} (Expected: False)")
    
    # Bob gets kicked/leaves and tries to rejoin
    stub.UserLeft(params) # Simulate disconnect
    check_rejoin = stub.ValidateJoin(params)
    print(f"  > Bob tries to Re-Join: Allowed={check_rejoin.allowed}, Reason='{check_rejoin.reason}' (Expected: Banned)")

    # --- 9. Clean Up ---
    print_step(9, "Charlie Leaves -> Room Empty -> Auto Delete")
    stub.UserLeft(params_c)
    print("  + Charlie Left")
    
    # Verify Deletion
    final_list = stub.ListRooms(service_pb2.Empty())
    room_found = any(r.id == room_id for r in final_list.rooms)
    print(f"  > Is Room {room_id} still listed? {room_found} (Expected: False)")

    print("\nTest Complete.")

if __name__ == "__main__":
    run_test()
