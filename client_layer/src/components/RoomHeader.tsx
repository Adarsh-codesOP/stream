import React from 'react';
import { ReadyState } from 'react-use-websocket/dist/lib/constants';

interface RoomHeaderProps {
    roomId: string | undefined;
    readyState: ReadyState;
    onLeave: () => void;
}

export const RoomHeader: React.FC<RoomHeaderProps> = ({ roomId, readyState, onLeave }) => {
    const connectionStatus = {
        [ReadyState.CONNECTING]: 'Connecting',
        [ReadyState.OPEN]: 'Open',
        [ReadyState.CLOSING]: 'Closing',
        [ReadyState.CLOSED]: 'Closed',
        [ReadyState.UNINSTANTIATED]: 'Uninstantiated',
    }[readyState] ?? 'Unknown';

    return (
        <header className="room-header">
            <div className="room-info">
                <h3>Room #{roomId}</h3>
                <span className={`status-badge ${connectionStatus.toLowerCase()}`}>{connectionStatus}</span>
            </div>
            <button className="leave-btn" onClick={onLeave}>Leave</button>
        </header>
    );
};
