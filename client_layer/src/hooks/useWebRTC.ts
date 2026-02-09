import { useState, useEffect, useRef, useCallback } from 'react';
import { useWebSocket } from 'react-use-websocket/dist/lib/use-websocket';


interface WebRTCProps {
    roomId: string;
    userId: string;
    onConnect?: () => void;
}

export const useWebRTC = ({ roomId, userId, onConnect }: WebRTCProps) => {
    const [messages, setMessages] = useState<any[]>([]);
    const [peers, setPeers] = useState<string[]>([]);
    const [users, setUsers] = useState<string[]>([]);

    // Refs for non-rendering state
    const localVideoRef = useRef<HTMLVideoElement>(null);
    const peerConnections = useRef<{ [key: string]: RTCPeerConnection }>({});
    const localStream = useRef<MediaStream | null>(null);
    const remoteVideoRefs = useRef<{ [key: string]: HTMLVideoElement | null }>({});

    const WS_URL = `ws://localhost:8001/ws/${roomId}/${userId}`;

    const { sendMessage, lastMessage, readyState } = useWebSocket(WS_URL, {
        onOpen: () => {
            console.log('Connected to Signaling Server');
            startLocalVideo();
            onConnect?.();
        },
        onClose: (event) => {
            console.log('Disconnected from Signaling Server', event);
            if (event.code === 4003 || event.code === 1008) {
                alert(`Disconnected: ${event.reason || "You have been blocked/kicked."}`);
                window.location.href = '/rooms'; // Force redirect
            }
        },
        onError: (event) => {
            console.error('WebSocket Error:', event);
        },
        shouldReconnect: (event) => event.code !== 4003 && event.code !== 1008, // Don't reconnect if blocked
    });

    const startLocalVideo = async () => {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: true });
            localStream.current = stream;
            if (localVideoRef.current) {
                localVideoRef.current.srcObject = stream;
            }
        } catch (err) {
            console.error("Error accessing media devices:", err);
        }
    };

    // --- WebRTC Logic ---

    const createPeerConnection = useCallback((targetUserId: string) => {
        if (peerConnections.current[targetUserId]) return peerConnections.current[targetUserId];

        const pc = new RTCPeerConnection({
            iceServers: [{ urls: 'stun:stun.l.google.com:19302' }]
        });

        if (localStream.current) {
            localStream.current.getTracks().forEach(track => {
                pc.addTrack(track, localStream.current!);
            });
        }

        pc.onicecandidate = (event) => {
            if (event.candidate) {
                sendMessage(JSON.stringify({
                    type: 'candidate',
                    target_id: targetUserId,
                    data: event.candidate
                }));
            }
        };

        pc.ontrack = (event) => {
            const vid = remoteVideoRefs.current[targetUserId];
            if (vid) {
                vid.srcObject = event.streams[0];
            }
        };

        peerConnections.current[targetUserId] = pc;
        return pc;
    }, [sendMessage]);

    // --- Signal Handling ---

    useEffect(() => {
        if (lastMessage !== null) {
            const msg = JSON.parse(lastMessage.data);
            const senderId = String(msg.user_id);
            const myId = String(userId);

            // Handle non-sender specific messages first if any
            if (msg.type === 'existing_users') {
                const existingIds = msg.ids.map(String);
                setUsers(existingIds);
                // Also add ourselves if not in list
                if (!existingIds.includes(myId)) {
                    setUsers(prev => [...prev, myId]);
                }
                return;
            }

            if (senderId === myId && msg.type !== 'chat') return;

            switch (msg.type) {
                case 'chat':
                    setMessages((prev) => [...prev, msg]);
                    break;
                case 'user_joined':
                    {
                        console.log(`User ${senderId} joined.`);
                        setUsers(prev => prev.includes(senderId) ? prev : [...prev, senderId]);

                        const pc = createPeerConnection(senderId);
                        pc.createOffer().then(offer => {
                            pc.setLocalDescription(offer);
                            sendMessage(JSON.stringify({ type: 'offer', target_id: senderId, data: offer }));
                        });
                        setPeers(prev => [...prev, senderId]);
                    }
                    break;
                case 'offer':
                    if (String(msg.target_id) === myId || !msg.target_id) {
                        const pc = createPeerConnection(senderId);
                        pc.setRemoteDescription(new RTCSessionDescription(msg.data))
                            .then(() => pc.createAnswer())
                            .then(answer => {
                                pc.setLocalDescription(answer);
                                sendMessage(JSON.stringify({ type: 'answer', target_id: senderId, data: answer }));
                            });
                        setPeers(prev => prev.includes(senderId) ? prev : [...prev, senderId]);
                    }
                    break;
                case 'answer':
                    if (String(msg.target_id) === myId) {
                        const pc = peerConnections.current[senderId];
                        if (pc) pc.setRemoteDescription(new RTCSessionDescription(msg.data));
                    }
                    break;
                case 'candidate':
                    if (String(msg.target_id) === myId) {
                        const pc = peerConnections.current[senderId];
                        if (pc) pc.addIceCandidate(new RTCIceCandidate(msg.data));
                    }
                    break;
                case 'user_left':
                    if (peerConnections.current[senderId]) {
                        peerConnections.current[senderId].close();
                        delete peerConnections.current[senderId];
                    }
                    setPeers(prev => prev.filter(id => id !== senderId));
                    setUsers(prev => prev.filter(id => id !== senderId));
                    break;
            }
        }
    }, [lastMessage, createPeerConnection, userId, sendMessage]);

    // Cleanup
    useEffect(() => {
        return () => {
            localStream.current?.getTracks().forEach(track => track.stop());
            Object.values(peerConnections.current).forEach(pc => pc.close());
        };
    }, []);

    const setRemoteRef = (id: string, el: HTMLVideoElement | null) => {
        remoteVideoRefs.current[id] = el;
    };

    return {
        messages,
        setMessages,
        peers,
        users,
        localVideoRef,
        setRemoteRef,
        sendMessage,
        readyState
    };
};
