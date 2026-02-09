import { useNavigate, useParams } from 'react-router-dom';
import { useWebRTC } from '../hooks/useWebRTC';
import { RoomHeader } from '../components/RoomHeader';
import { VideoGrid } from '../components/VideoGrid';
import { ChatSidebar } from '../components/ChatSidebar';
import { UserList } from '../components/UserList';
import { useEffect, useState } from 'react';
import { api, endpoints } from '../api';

function ChatRoom() {
    const { roomId } = useParams();
    const navigate = useNavigate();
    const userId = localStorage.getItem('user_id');
    const [roomCreatorId, setRoomCreatorId] = useState<string | null>(null);

    const {
        messages,
        peers,
        users,
        localVideoRef,
        setRemoteRef,
        sendMessage,
        readyState
    } = useWebRTC({
        roomId: roomId!,
        userId: userId!
    });

    useEffect(() => {
        const fetchRoomDetails = async () => {
            try {
                const response = await api.get(`${endpoints.rooms}/${roomId}`);
                setRoomCreatorId(String(response.data.created_by));
            } catch (error) {
                console.error("Failed to fetch room details:", error);
            }
        };
        if (roomId) {
            fetchRoomDetails();
        }
    }, [roomId]);

    const handleSendMessage = (text: string) => {
        sendMessage(JSON.stringify({ type: 'chat', content: text }));
    };

    const handleLeave = () => {
        navigate('/rooms');
    };

    const handleBlockUser = async (targetUserId: string) => {
        if (!confirm(`Are you sure you want to block User ${targetUserId}?`)) return;

        try {
            await api.post(`${endpoints.rooms}/${roomId}/block`, null, {
                params: {
                    user_to_block_id: targetUserId,
                    reason: "Blocked by admin"
                }
            });
            alert(`User ${targetUserId} has been blocked.`);
        } catch (error: any) {
            alert(`Failed to block user: ${error.response?.data?.detail || "Unknown error"}`);
        }
    };

    return (
        <div className="room-layout">
            <UserList
                users={users}
                currentUserId={userId}
                roomCreatorId={roomCreatorId}
                onBlockUser={handleBlockUser}
            />
            <div className="video-section">
                <RoomHeader
                    roomId={roomId}
                    readyState={readyState}
                    onLeave={handleLeave}
                />
                <VideoGrid
                    localVideoRef={localVideoRef}
                    peers={peers}
                    setRemoteRef={setRemoteRef}
                />
            </div>
            <ChatSidebar
                messages={messages}
                userId={userId}
                onSend={handleSendMessage}
                readyState={readyState}
            />
        </div>
    );
}

export default ChatRoom;
