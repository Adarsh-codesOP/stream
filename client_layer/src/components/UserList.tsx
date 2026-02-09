import React from 'react';

interface UserListProps {
    users: string[]; // List of user IDs
    currentUserId: string | null;
    roomCreatorId: string | null;
    onBlockUser: (userId: string) => void;
}

export const UserList: React.FC<UserListProps> = ({ users, currentUserId, roomCreatorId, onBlockUser }) => {
    const isAdmin = String(currentUserId) === String(roomCreatorId);

    return (
        <div className="user-list-container">
            <h3>Participants ({users.length})</h3>
            <ul className="user-list">
                {users.map(userId => (
                    <li key={userId} className="user-item">
                        <span className="user-name">
                            User {userId} {String(userId) === String(currentUserId) && "(You)"}
                            {String(userId) === String(roomCreatorId) && <span className="admin-badge">Admin</span>}
                        </span>

                        {isAdmin && String(userId) !== String(currentUserId) && (
                            <button
                                className="block-btn"
                                onClick={() => onBlockUser(userId)}
                                title="Block Control"
                            >
                                Block
                            </button>
                        )}
                    </li>
                ))}
            </ul>
        </div>
    );
};
