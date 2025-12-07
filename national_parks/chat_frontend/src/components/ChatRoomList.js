import React from 'react';
import './ChatRoomList.css';

function ChatRoomList({ rooms, onSelectRoom, onRefresh }) {
  return (
    <div className="chat-room-list">
      <div className="room-list-header">
        <h2>Available Chat Rooms</h2>
        <button onClick={onRefresh} className="refresh-btn">
          🔄 Refresh
        </button>
      </div>
      
      {rooms.length === 0 ? (
        <div className="empty-state">
          <p>No chat rooms available at the moment</p>
          <p className="hint">Create a new room to get started!</p>
        </div>
      ) : (
        <div className="rooms-grid">
          {rooms.map((room) => (
            <div
              key={room.id}
              className="room-card"
              onClick={() => onSelectRoom(room)}
            >
              <div className="room-header">
                <h3>{room.name}</h3>
                {room.is_public ? (
                  <span className="public-badge">Public</span>
                ) : (
                  <span className="private-badge">Private</span>
                )}
              </div>
              {room.description && (
                <p className="room-description">{room.description}</p>
              )}
              <div className="room-stats">
                <span>💬 {room.message_count || 0} messages</span>
                <span>👥 {room.participants?.length || 0} participants</span>
              </div>
              {room.last_message && (
                <div className="last-message">
                  <strong>{room.last_message.user}:</strong> {room.last_message.content}
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default ChatRoomList;

