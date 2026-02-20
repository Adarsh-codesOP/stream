from database import SessionLocal
from models import Room

def remove_room():
    db = SessionLocal()
    room = db.query(Room).filter(Room.name == "hii").first()
    if room:
        db.delete(room)
        db.commit() 
        print("Room hii removed")
    else:
        print("Room hii not found")

if __name__ == "__main__":
    remove_room()
