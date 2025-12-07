# QUICK FIX: no such table: chat_chatroom_participants

## The Error:
```
OperationalError: no such table: chat_chatroom_participants
```

## Solution:

### Option 1: Using PyCharm Terminal
1. Open PyCharm
2. Open Terminal (bottom panel)
3. Make sure you're in: `C:\Users\Yaron\PycharmProjects\backend\NationalParks\national_parks`
4. Run:
   ```bash
   python manage.py migrate chat
   ```

### Option 2: Using Command Prompt
1. Open Command Prompt (cmd)
2. Navigate to project:
   ```bash
   cd C:\Users\Yaron\PycharmProjects\backend\NationalParks\national_parks
   ```
3. Activate virtual environment (if exists):
   ```bash
   ..\venv\Scripts\activate
   # OR
   venv\Scripts\activate
   ```
4. Run migrations:
   ```bash
   python manage.py migrate chat
   ```

### Option 3: Using the batch file
1. Double-click: `RUN_MIGRATIONS.bat` in the project root

## What to expect:
You should see output like:
```
Operations to perform:
  Apply all migrations: chat
Running migrations:
  Applying chat.0001_initial... OK
```

## After migrations:
1. **Restart your Django server** (stop and start again)
2. Test: http://localhost:8001/api/chat/rooms/
3. Should return `[]` instead of 500 error

## Still not working?
Check:
- Is Django installed? `pip list | findstr Django`
- Is the database file accessible? Check `db.sqlite3` exists
- Are you in the right directory? `dir manage.py` should show the file

