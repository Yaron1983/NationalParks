import React, { useState, useEffect } from 'react';
import './App.css';
import ChatRoomList from './components/ChatRoomList';
import ChatRoom from './components/ChatRoom';
import CreateRoomModal from './components/CreateRoomModal';
import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8001/api/chat';

function App() {
  const [rooms, setRooms] = useState([]);
  const [selectedRoom, setSelectedRoom] = useState(null);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchRooms();
  }, []);

  const fetchRooms = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API_BASE_URL}/rooms/`);
      setRooms(response.data);
      setError(null);
    } catch (err) {
      setError('Error loading chat rooms');
      console.error('Error fetching rooms:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateRoom = async (roomData) => {
    try {
      const response = await axios.post(`${API_BASE_URL}/rooms/`, roomData, {
        headers: {
          'Content-Type': 'application/json',
        },
        withCredentials: true,
      });
      setRooms([response.data, ...rooms]);
      setSelectedRoom(response.data);
      setShowCreateModal(false);
    } catch (err) {
      setError('Error creating chat room');
      console.error('Error creating room:', err);
    }
  };

  const handleSelectRoom = (room) => {
    setSelectedRoom(room);
  };

  const handleBackToList = () => {
    setSelectedRoom(null);
    fetchRooms();
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>💬 Chat Rooms - National Parks</h1>
        {!selectedRoom && (
          <button 
            className="create-room-btn"
            onClick={() => setShowCreateModal(true)}
          >
            + Create New Room
          </button>
        )}
      </header>

      {error && (
        <div className="error-message">
          {error}
        </div>
      )}

      {loading && !selectedRoom ? (
        <div className="loading">Loading...</div>
      ) : selectedRoom ? (
        <ChatRoom 
          room={selectedRoom} 
          onBack={handleBackToList}
          apiBaseUrl={API_BASE_URL}
        />
      ) : (
        <ChatRoomList 
          rooms={rooms} 
          onSelectRoom={handleSelectRoom}
          onRefresh={fetchRooms}
        />
      )}

      {showCreateModal && (
        <CreateRoomModal
          onClose={() => setShowCreateModal(false)}
          onCreate={handleCreateRoom}
        />
      )}
    </div>
  );
}

export default App;

