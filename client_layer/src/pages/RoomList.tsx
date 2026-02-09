import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { api, endpoints } from '../api';

interface Room {
    id: number;
    name: string;
    max_participants: number;
}

function RoomList() {
    const [rooms, setRooms] = useState<Room[]>([]);
    const [newRoomName, setNewRoomName] = useState('');
    const navigate = useNavigate();
    const username = localStorage.getItem('username');

    useEffect(() => {
        fetchRooms();
    }, []);

    const fetchRooms = async () => {
        try {
            const res = await api.get(endpoints.rooms);
            setRooms(res.data);
        } catch (err) {
            console.error(err);
        }
    };

    const createRoom = async (e: React.FormEvent) => {
        e.preventDefault();
        try {
            await api.post(endpoints.createRoom, {
                name: newRoomName,
                max_participants: 10
            });
            setNewRoomName('');
            fetchRooms();
        } catch (err) {
            console.error(err);
        }
    };

    const joinRoom = (roomId: number) => {
        navigate(`/room/${roomId}`);
    };

    return (
        <div className="room-list-container">
            <div className="room-list-header">
                <h2>StreamLink Lobby</h2>
                <span>Welcome, {username}</span>
            </div>

            <div className="room-card" style={{ marginBottom: '2rem' }}>
                <h3>Create New Room</h3>
                <form onSubmit={createRoom}>
                    <input
                        type="text"
                        placeholder="Room Name"
                        value={newRoomName}
                        onChange={(e) => setNewRoomName(e.target.value)}
                        required
                    />
                    <button type="submit" className="create-room-btn">Create</button>
                </form>
            </div>

            <div className="grid-container">
                {rooms.map((room) => (
                    <div key={room.id} className="room-item" onClick={() => joinRoom(room.id)}>
                        <h3>{room.name}</h3>
                        <p>Max: {room.max_participants}</p>
                        <button className="join-btn" style={{ marginTop: '1rem', width: '100%' }}>Join</button>
                    </div>
                ))}
            </div>
            {rooms.length === 0 && <p style={{ color: 'var(--text-dim)' }}>No rooms available. Create one to get started!</p>}
        </div>
    );
}

export default RoomList;
