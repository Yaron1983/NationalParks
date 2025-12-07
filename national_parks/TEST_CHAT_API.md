# Test Chat API on Port 8001

## Quick Test:

1. **Open browser console** (F12)

2. **Test API endpoint:**
   ```javascript
   fetch('/api/chat/rooms/')
     .then(r => r.json())
     .then(data => console.log('Rooms:', data))
     .catch(err => console.error('Error:', err));
   ```

3. **Check response:**
   - If you see `[]` (empty array) - API works, just no rooms
   - If you see error - check migrations and server

4. **Verify migrations ran:**
   ```bash
   python manage.py migrate chat
   ```

5. **Create a test room via admin:**
   - Go to: http://localhost:8001/admin/
   - Login
   - Chat → Chat rooms → Add chat room
   - Create a public room named "General"

6. **Test again:**
   - Refresh the chat widget
   - Should see the room now

## Common Issues:

- **404 Not Found**: Check URL routing in `urls.py`
- **500 Error**: Check migrations - run `python manage.py migrate chat`
- **CORS Error**: Shouldn't happen on same origin, but check CORS settings
- **Empty array**: Normal if no rooms exist - create one via admin

