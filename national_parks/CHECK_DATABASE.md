# Check Database Status

Since migrations say "No migrations to apply" but table doesn't exist, let's check:

## Step 1: Check if migration was actually applied

Run in PyCharm terminal:
```bash
python manage.py showmigrations chat
```

You should see:
```
chat
 [X] 0001_initial
```

If you see `[ ]` (unchecked), the migration wasn't applied.

## Step 2: Check what tables exist

Run:
```bash
python manage.py dbshell
```

Then in SQLite shell:
```sql
.tables
```

Look for:
- `chat_chatroom`
- `chat_message`
- `chat_chatroom_participants` (this is what's missing!)

## Step 3: If migration shows as applied but table doesn't exist

This is a migration state issue. Try:

```bash
# Fake unapply the migration
python manage.py migrate chat 0001 --fake

# Then reapply it
python manage.py migrate chat
```

## Step 4: Alternative - Reset migrations

If above doesn't work:

```bash
# Delete migration record (but keep the file)
python manage.py migrate chat zero --fake

# Reapply
python manage.py migrate chat
```

## Step 5: Check database file

Make sure you're using the correct database:
- Check `settings.py` - DATABASES['default']['NAME']
- Should point to: `BASE_DIR / 'db.sqlite3'`
- Make sure this file exists and is writable

