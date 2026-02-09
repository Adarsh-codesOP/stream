import React from 'react';

interface VideoGridProps {
    localVideoRef: React.RefObject<HTMLVideoElement | null>;
    peers: string[];
    setRemoteRef: (id: string, el: HTMLVideoElement | null) => void;
}

export const VideoGrid: React.FC<VideoGridProps> = ({ localVideoRef, peers, setRemoteRef }) => {
    return (
        <div className="video-grid">
            <div className="video-card local">
                <video ref={localVideoRef as React.RefObject<HTMLVideoElement>} autoPlay muted playsInline />
                <div className="video-overlay">You</div>
            </div>
            {peers.map(peerId => (
                <div key={peerId} className="video-card">
                    <video
                        ref={(el) => setRemoteRef(peerId, el)}
                        autoPlay
                        playsInline
                    />
                    <div className="video-overlay">User {peerId}</div>
                </div>
            ))}
        </div>
    );
};
