# Fix: no such table: chat_chatroom_participants

This error occurs because the database migrations haven't been run yet.

## Solution:

Run these commands in your terminal:

```bash
# Navigate to the national_parks directory
cd national_parks

# Create migrations (if needed)
python manage.py makemigrations chat

# Apply migrations to create the tables
python manage.py migrate chat

# Or migrate all apps
python manage.py migrate
```

## What this does:

1. `makemigrations chat` - Creates migration files for the chat app
2. `migrate chat` - Applies the migrations and creates the database tables including:
   - `chat_chatroom` - Chat rooms table
   - `chat_message` - Messages table
   - `chat_chatroom_participants` - Many-to-many relationship table for room participants

## After running migrations:

The error should be resolved and you can use the chat functionality.

