# Debug: Error loading rooms in chat widget

## Common Issues and Solutions:

### 1. Migrations not run
**Error:** `no such table: chat_chatroom_participants`

**Solution:**
```bash
cd national_parks
python manage.py migrate chat
```

### 2. No rooms in database
If migrations ran but there are no rooms, the widget will show "No rooms available" which is normal.

**To create a test room:**
- Go to http://localhost:8000/admin/
- Login as admin
- Go to Chat > Chat rooms
- Add a new chat room

### 3. API endpoint not accessible
**Check if API works:**
- Open browser console (F12)
- Try: `fetch('/api/chat/rooms/').then(r => r.json()).then(console.log)`
- Check for CORS errors or 404/500 errors

### 4. Check browser console
Open browser console (F12) and look for:
- Network errors
- CORS errors
- JavaScript errors

### 5. Verify server is running
Make sure Django server is running:
```bash
python manage.py runserver
# or
daphne -b 0.0.0.0 -p 8000 national_parks.asgi:application
```

### 6. Check URL path
The widget tries to fetch from: `/api/chat/rooms/`
Make sure this matches your URL configuration in `national_parks/urls.py`

