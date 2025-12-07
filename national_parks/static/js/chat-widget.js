// Floating Chat Widget
class ChatWidget {
  constructor() {
    this.isOpen = false;
    this.currentRoom = null;
    this.ws = null;
    this.rooms = [];
    this.messages = [];
    this.init();
  }

  init() {
    this.createWidget();
    this.loadRooms();
  }

  createWidget() {
    const widget = document.createElement('div');
    widget.className = 'floating-chat-widget';
    widget.innerHTML = `
      <button class="chat-toggle-btn" id="chat-toggle">💬</button>
      <div class="chat-widget-container" id="chat-widget">
        <div class="chat-widget-header">
          <h3 id="chat-header-title">Chat Rooms</h3>
          <div class="chat-widget-header-actions">
            <button class="chat-widget-create-btn" id="chat-create-room" title="Create Room">+</button>
            <button class="chat-widget-back-btn" id="chat-back" style="display: none;" title="Back to Rooms">←</button>
            <button class="chat-widget-close" id="chat-close">×</button>
          </div>
        </div>
        <div class="chat-widget-rooms" id="chat-rooms">
          <div class="chat-widget-loading">Loading rooms...</div>
        </div>
        <div class="chat-widget-messages" id="chat-messages" style="display: none;">
          <div class="chat-widget-status" id="chat-status">
            <span class="chat-widget-status-indicator disconnected"></span>
            <span>Connecting...</span>
          </div>
          <div id="chat-messages-list"></div>
        </div>
        <div class="chat-widget-input-area" id="chat-input-area" style="display: none;">
          <input type="text" class="chat-widget-input" id="chat-input" placeholder="Type a message...">
          <button class="chat-widget-send" id="chat-send">Send</button>
        </div>
      </div>
    `;
    document.body.appendChild(widget);

    document.getElementById('chat-toggle').addEventListener('click', () => this.toggle());
    document.getElementById('chat-close').addEventListener('click', () => this.close());
    document.getElementById('chat-create-room').addEventListener('click', () => this.showCreateRoomModal());
    document.getElementById('chat-back').addEventListener('click', () => this.backToRooms());
    document.getElementById('chat-send').addEventListener('click', () => this.sendMessage());
    document.getElementById('chat-input').addEventListener('keypress', (e) => {
      if (e.key === 'Enter') this.sendMessage();
    });
  }

  toggle() {
    this.isOpen = !this.isOpen;
    const widget = document.getElementById('chat-widget');
    const toggleBtn = document.getElementById('chat-toggle');
    
    if (this.isOpen) {
      widget.classList.add('open');
      toggleBtn.classList.add('active');
    } else {
      widget.classList.remove('open');
      toggleBtn.classList.remove('active');
      this.disconnect();
    }
  }

  close() {
    this.isOpen = false;
    const widget = document.getElementById('chat-widget');
    const toggleBtn = document.getElementById('chat-toggle');
    widget.classList.remove('open');
    toggleBtn.classList.remove('active');
    this.disconnect();
  }

  async loadRooms() {
    try {
      const response = await fetch('/api/chat/rooms/', {
        method: 'GET',
        headers: {
          'Accept': 'application/json',
        },
        credentials: 'same-origin'
      });
      
      if (!response.ok) {
        const errorText = await response.text();
        console.error('API Error:', response.status, errorText);
        throw new Error(`HTTP ${response.status}: ${errorText.substring(0, 100)}`);
      }
      
      const data = await response.json();
      this.rooms = Array.isArray(data) ? data : [];
      this.renderRooms();
    } catch (error) {
      console.error('Error loading rooms:', error);
      const errorMsg = error.message || 'Error loading rooms';
      document.getElementById('chat-rooms').innerHTML = 
        `<div class="chat-widget-empty">
          ${errorMsg}
          <br><br>
          <button onclick="window.chatWidget.loadRooms()" style="padding: 0.5rem 1rem; background: #667eea; color: white; border: none; border-radius: 6px; cursor: pointer;">
            Retry
          </button>
        </div>`;
    }
  }

  renderRooms() {
    const container = document.getElementById('chat-rooms');
    
    if (this.rooms.length === 0) {
      container.innerHTML = '<div class="chat-widget-empty">No rooms available<br><br>Click the + button to create one!</div>';
      return;
    }

    container.innerHTML = this.rooms.map(room => `
      <div class="chat-widget-room" data-room-id="${room.id}" data-room-name="${room.name}">
        <h4>${room.name}</h4>
        <p>💬 ${room.message_count || 0} messages</p>
        <p>👥 ${room.participants?.length || 0} participants</p>
      </div>
    `).join('');

    container.querySelectorAll('.chat-widget-room').forEach(roomEl => {
      roomEl.addEventListener('click', () => {
        const roomId = roomEl.dataset.roomId;
        const roomName = roomEl.dataset.roomName;
        this.selectRoom(roomId, roomName);
      });
    });
  }

  selectRoom(roomId, roomName) {
    this.currentRoom = { id: roomId, name: roomName };
    
    // Update UI
    document.querySelectorAll('.chat-widget-room').forEach(el => {
      el.classList.remove('active');
      if (el.dataset.roomId === roomId) {
        el.classList.add('active');
      }
    });

    document.getElementById('chat-rooms').style.display = 'none';
    document.getElementById('chat-messages').style.display = 'flex';
    document.getElementById('chat-input-area').style.display = 'flex';
    document.getElementById('chat-create-room').style.display = 'none';
    document.getElementById('chat-back').style.display = 'block';
    document.getElementById('chat-header-title').textContent = roomName;

    this.loadMessages(roomId);
    this.connectWebSocket(roomName);
  }

  async loadMessages(roomId) {
    try {
      const response = await fetch(`/api/chat/messages/?room=${roomId}`, {
        method: 'GET',
        headers: {
          'Accept': 'application/json',
        },
        credentials: 'same-origin'
      });
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }
      
      const data = await response.json();
      this.messages = Array.isArray(data) ? data : [];
      this.renderMessages();
    } catch (error) {
      console.error('Error loading messages:', error);
      const container = document.getElementById('chat-messages-list');
      if (container) {
        container.innerHTML = `<div class="chat-widget-empty">Error loading messages: ${error.message}</div>`;
      }
    }
  }

  renderMessages() {
    const container = document.getElementById('chat-messages-list');
    
    if (this.messages.length === 0) {
      container.innerHTML = '<div class="chat-widget-empty">No messages yet</div>';
      return;
    }

    container.innerHTML = this.messages.map(msg => `
      <div class="chat-widget-message">
        <div class="chat-widget-message-header">
          <span class="chat-widget-message-user">${msg.user?.username || 'Anonymous'}</span>
          <span class="chat-widget-message-time">${this.formatTime(msg.timestamp)}</span>
        </div>
        <div class="chat-widget-message-content">${msg.content}</div>
      </div>
    `).join('');

    container.scrollTop = container.scrollHeight;
  }

  connectWebSocket(roomName) {
    this.disconnect();

    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/ws/chat/${roomName}/`;
    
    this.ws = new WebSocket(wsUrl);

    this.ws.onopen = () => {
      const status = document.getElementById('chat-status');
      status.innerHTML = `
        <span class="chat-widget-status-indicator connected"></span>
        <span>Connected</span>
      `;
    };

    this.ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      
      if (data.type === 'chat_message') {
        const message = {
          id: data.message_id,
          content: data.message,
          user: { username: data.username },
          timestamp: data.timestamp
        };
        this.messages.push(message);
        this.renderMessages();
      }
    };

    this.ws.onerror = (error) => {
      console.error('WebSocket error:', error);
      const status = document.getElementById('chat-status');
      status.innerHTML = `
        <span class="chat-widget-status-indicator disconnected"></span>
        <span>Connection error</span>
      `;
    };

    this.ws.onclose = () => {
      const status = document.getElementById('chat-status');
      status.innerHTML = `
        <span class="chat-widget-status-indicator disconnected"></span>
        <span>Disconnected</span>
      `;
    };
  }

  disconnect() {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }

  sendMessage() {
    const input = document.getElementById('chat-input');
    const message = input.value.trim();
    
    if (!message || !this.ws || this.ws.readyState !== WebSocket.OPEN) {
      return;
    }

    this.ws.send(JSON.stringify({
      type: 'chat_message',
      message: message
    }));

    input.value = '';
  }

  formatTime(timestamp) {
    const date = new Date(timestamp);
    return date.toLocaleTimeString('en-US', {
      hour: '2-digit',
      minute: '2-digit'
    });
  }

  backToRooms() {
    this.currentRoom = null;
    this.disconnect();
    
    document.getElementById('chat-rooms').style.display = 'block';
    document.getElementById('chat-messages').style.display = 'none';
    document.getElementById('chat-input-area').style.display = 'none';
    document.getElementById('chat-create-room').style.display = 'block';
    document.getElementById('chat-back').style.display = 'none';
    document.getElementById('chat-header-title').textContent = 'Chat Rooms';
    
    // Reload rooms to show any new ones
    this.loadRooms();
  }

  showCreateRoomModal() {
    const modal = document.createElement('div');
    modal.className = 'chat-widget-modal';
    modal.innerHTML = `
      <div class="chat-widget-modal-content">
        <div class="chat-widget-modal-header">
          <h3>Create New Room</h3>
          <button class="chat-widget-modal-close" onclick="this.closest('.chat-widget-modal').remove()">×</button>
        </div>
        <form id="create-room-form" class="chat-widget-modal-form">
          <div class="chat-widget-form-group">
            <label>Room Name *</label>
            <input type="text" id="room-name" required placeholder="e.g., General Discussion">
          </div>
          <div class="chat-widget-form-group">
            <label>Description (Optional)</label>
            <textarea id="room-description" rows="3" placeholder="Room description..."></textarea>
          </div>
          <div class="chat-widget-form-group">
            <label>
              <input type="checkbox" id="room-public" checked>
              Public room (everyone can join)
            </label>
          </div>
          <div class="chat-widget-form-actions">
            <button type="button" onclick="this.closest('.chat-widget-modal').remove()" class="chat-widget-btn-cancel">Cancel</button>
            <button type="submit" class="chat-widget-btn-submit">Create Room</button>
          </div>
        </form>
      </div>
    `;
    document.body.appendChild(modal);

    document.getElementById('create-room-form').addEventListener('submit', (e) => {
      e.preventDefault();
      this.createRoom(modal);
    });
  }

  async createRoom(modal) {
    const name = document.getElementById('room-name').value.trim();
    const description = document.getElementById('room-description').value.trim();
    const isPublic = document.getElementById('room-public').checked;

    if (!name) {
      alert('Room name is required');
      return;
    }

    try {
      const response = await fetch('/api/chat/rooms/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
          'X-CSRFToken': this.getCsrfToken(),
        },
        credentials: 'same-origin',
        body: JSON.stringify({
          name: name,
          description: description,
          is_public: isPublic
        })
      });

      if (!response.ok) {
        const error = await response.text();
        throw new Error(error || `HTTP ${response.status}`);
      }

      const newRoom = await response.json();
      
      // Add to rooms list
      this.rooms.unshift(newRoom);
      this.renderRooms();
      
      // Close modal
      modal.remove();
      
      // Select the new room
      this.selectRoom(newRoom.id, newRoom.name);
      
    } catch (error) {
      console.error('Error creating room:', error);
      alert(`Error creating room: ${error.message}`);
    }
  }

  getCsrfToken() {
    const cookies = document.cookie.split(';');
    for (let cookie of cookies) {
      const [name, value] = cookie.trim().split('=');
      if (name === 'csrftoken') {
        return value;
      }
    }
    // Try to get from meta tag
    const meta = document.querySelector('meta[name=csrf-token]');
    return meta ? meta.content : '';
  }
}

// Initialize chat widget when DOM is ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => {
    window.chatWidget = new ChatWidget();
  });
} else {
  window.chatWidget = new ChatWidget();
}

