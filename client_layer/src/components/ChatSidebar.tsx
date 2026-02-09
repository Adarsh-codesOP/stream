import React, { useState } from 'react';
import { ReadyState } from 'react-use-websocket/dist/lib/constants';

interface ChatSidebarProps {
    messages: any[];
    userId: string | null;
    onSend: (text: string) => void;
    readyState: ReadyState;
}

export const ChatSidebar: React.FC<ChatSidebarProps> = ({ messages, userId, onSend, readyState }) => {
    const [inputText, setInputText] = useState('');

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        if (inputText.trim()) {
            onSend(inputText);
            setInputText('');
        }
    };

    return (
        <aside className="chat-sidebar">
            <div className="chat-header-simple">
                <h4>Chat</h4>
            </div>
            <div className="chat-messages">
                {messages.length === 0 && <div className="empty-state">No messages yet.</div>}
                {messages.map((msg, idx) => (
                    <div key={idx} className={`chat-bubble ${String(msg.user_id) === String(userId) ? 'mine' : 'theirs'}`}>
                        <div className="bubble-content">
                            {String(msg.user_id) !== String(userId) && <span className="sender-name">User {msg.user_id}</span>}
                            <p>{msg.content}</p>
                        </div>
                    </div>
                ))}
            </div>
            <form className="chat-input-area" onSubmit={handleSubmit}>
                <input
                    type="text"
                    value={inputText}
                    onChange={(e) => setInputText(e.target.value)}
                    placeholder="Say something..."
                    disabled={readyState !== ReadyState.OPEN}
                />
            </form>
        </aside>
    );
};
