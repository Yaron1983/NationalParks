import React, { useState, useEffect, useRef } from 'react';
import './ChatRoom.css';
import axios from 'axios';

function ChatRoom({ room, onBack, apiBaseUrl }) {
  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState('');
  const [ws, setWs] = useState(null);
  const [connected, setConnected] = useState(false);
  const [loading, setLoading] = useState(true);
  const messagesEndRef = useRef(null);
  const wsRef = useRef(null);

  useEffect(() => {
    fetchMessages();
    connectWebSocket();

    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, [room.id]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const fetchMessages = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${apiBaseUrl}/messages/?room=${room.id}`);
      setMessages(response.data);
    } catch (err) {
      console.error('Error fetching messages:', err);
    } finally {
      setLoading(false);
    }
  };

  const connectWebSocket = () => {
  const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';

  // חובה! לקודד את שם החדר
  const encodedRoom = encodeURIComponent(room.name);

  const wsUrl = `${protocol}//${window.location.host}/ws/chat/${encodedRoom}/`;
  console.log(wsUrl)
  const websocket = new WebSocket(wsUrl);
  wsRef.current = websocket;

  websocket.onopen = () => {
    setConnected(true);
    console.log('WebSocket connected');
  };

  websocket.onmessage = (event) => {
    const data = JSON.parse(event.data);

    if (data.type === 'chat_message') {
      const message = {
        id: data.message_id,
        content: data.message,
        user: {
          id: data.user_id,
          username: data.username,
        },
        timestamp: data.timestamp,
      };
      setMessages((prev) => [...prev, message]);
    } else if (data.type === 'room_info') {
      console.log('Room info:', data);
    }
  };

  websocket.onerror = (error) => {
    console.error('WebSocket error:', error);
    setConnected(false);
  };

  websocket.onclose = () => {
    setConnected(false);
    console.log('WebSocket disconnected');

    // Attempt to reconnect after 3 seconds
    setTimeout(() => {
      if (room.id) {
        connectWebSocket();
      }
    }, 3000);
  };

  setWs(websocket);
};

  const sendMessage = async (e) => {
    e.preventDefault();
    if (!newMessage.trim() || !connected) return;

    try {
      const messageData = {
        type: 'chat_message',
        message: newMessage.trim(),
      };

      if (ws && ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify(messageData));
        setNewMessage('');
      }
    } catch (err) {
      console.error('Error sending message:', err);
    }
  };

  const formatTime = (timestamp) => {
    const date = new Date(timestamp);
    return date.toLocaleTimeString('he-IL', {
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  return (
    <div className="chat-room">
      <div className="chat-header">
        <button onClick={onBack} className="back-btn">
          ← Back to List
        </button>
        <div className="room-info">
          <h2>{room.name}</h2>
          <div className="connection-status">
            <span className={`status-indicator ${connected ? 'connected' : 'disconnected'}`}></span>
            {connected ? 'Connected' : 'Connecting...'}
          </div>
        </div>
      </div>

      <div className="messages-container">
        {loading ? (
          <div className="loading-messages">Loading messages...</div>
        ) : messages.length === 0 ? (
          <div className="no-messages">
            <p>No messages in this room yet</p>
            <p className="hint">Be the first to write!</p>
          </div>
        ) : (
          <div className="messages-list">
            {messages.map((message) => (
              <div key={message.id} className="message">
                <div className="message-header">
                  <strong className="message-user">{message.user?.username || 'Anonymous'}</strong>
                  <span className="message-time">{formatTime(message.timestamp)}</span>
                </div>
                <div className="message-content">{message.content}</div>
              </div>
            ))}
            <div ref={messagesEndRef} />
          </div>
        )}
      </div>

      <form onSubmit={sendMessage} className="message-form">
        <input
          type="text"
          value={newMessage}
          onChange={(e) => setNewMessage(e.target.value)}
          placeholder={connected ? "Type a message..." : "Connecting..."}
          disabled={!connected}
          className="message-input"
        />
        <button
          type="submit"
          disabled={!connected || !newMessage.trim()}
          className="send-btn"
        >
          Send
        </button>
      </form>
    </div>
  );
}

export default ChatRoom;

