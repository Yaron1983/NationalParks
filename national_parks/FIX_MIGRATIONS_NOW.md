# URGENT: Fix "no such table: chat_chatroom_participants"

## The Problem:
You're getting a 500 error because the database tables for the chat app don't exist yet.

## Solution - Run these commands:

### Step 1: Activate your virtual environment
If you're using a virtual environment (venv), activate it first:

**Windows:**
```bash
# If venv is in the project root:
venv\Scripts\activate

# Or if it's in national_parks:
cd national_parks
venv\Scripts\activate
```

**Or if using conda:**
```bash
conda activate your_env_name
```

### Step 2: Navigate to the project
```bash
cd C:\Users\Yaron\PycharmProjects\backend\NationalParks\national_parks
```

### Step 3: Run migrations
```bash
python manage.py migrate chat
```

**Or migrate all apps:**
```bash
python manage.py migrate
```

## What this creates:
- `chat_chatroom` - Chat rooms table
- `chat_message` - Messages table  
- `chat_chatroom_participants` - Many-to-many relationship table (this is what's missing!)

## After running migrations:
1. Restart your Django server
2. The chat widget should work now
3. You can create rooms via admin panel

## Quick Test:
After migrations, test the API:
- Open: http://localhost:8001/api/chat/rooms/
- Should return `[]` (empty array) instead of 500 error

