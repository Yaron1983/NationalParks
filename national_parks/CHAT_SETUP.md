# הוראות התקנה - מערכת חדרי צ'ט

מערכת חדרי צ'ט עם WebSockets ו-React.

## דרישות

- Python 3.8+
- Node.js 14+ ו-npm
- Django 5.2.5
- Django Channels

## התקנת Backend

1. התקן את התלויות:
```bash
cd national_parks
pip install -r requirements.txt
```

2. הכן את מסד הנתונים:
```bash
python manage.py makemigrations chat
python manage.py migrate
```

3. צור משתמש מנהל (אם עדיין לא):
```bash
python manage.py createsuperuser
```

4. הפעל את השרת עם Daphne (תמיכה ב-WebSockets):
```bash
daphne -b 0.0.0.0 -p 8000 national_parks.asgi:application
```

או עם runserver (לפיתוח בלבד):
```bash
python manage.py runserver
```

## התקנת Frontend

1. עבור לתיקיית הפרונטאנד:
```bash
cd chat_frontend
```

2. התקן את התלויות:
```bash
npm install
```

3. הפעל את השרת:
```bash
npm start
```

האפליקציה תרוץ על http://localhost:3000

## שימוש

### יצירת חדר צ'ט

1. לחץ על "צור חדר חדש"
2. מלא את פרטי החדר:
   - שם החדר (חובה)
   - תיאור (אופציונלי)
   - האם החדר ציבורי או פרטי
3. לחץ על "צור חדר"

### הצטרפות לחדר

1. בחר חדר מהרשימה
2. החדר ייפתח עם כל ההודעות הקודמות
3. כתוב הודעה ושלח

### תכונות

- **הודעות בזמן אמת**: כל ההודעות מופיעות מיד לכל המחוברים
- **חדרים ציבוריים ופרטיים**: אפשר ליצור חדרים ציבוריים או פרטיים
- **מצב חיבור**: אינדיקטור מצב חיבור ל-WebSocket
- **היסטוריית הודעות**: כל ההודעות נשמרות במסד הנתונים

## API Endpoints

### Chat Rooms

- `GET /api/chat/rooms/` - רשימת כל החדרים
- `POST /api/chat/rooms/` - יצירת חדר חדש
- `GET /api/chat/rooms/{id}/` - פרטי חדר
- `PUT /api/chat/rooms/{id}/` - עדכון חדר
- `DELETE /api/chat/rooms/{id}/` - מחיקת חדר
- `POST /api/chat/rooms/{id}/join/` - הצטרפות לחדר
- `POST /api/chat/rooms/{id}/leave/` - יציאה מחדר

### Messages

- `GET /api/chat/messages/?room={room_id}` - הודעות של חדר מסוים
- `POST /api/chat/messages/` - יצירת הודעה חדשה

### WebSocket

- `ws://localhost:8000/ws/chat/{room_name}/` - חיבור WebSocket לחדר

## הגדרות

### CORS (אם צריך)

אם הפרונטאנד רץ על פורט אחר, יש להוסיף CORS:

```bash
pip install django-cors-headers
```

ואז ב-`settings.py`:
```python
INSTALLED_APPS = [
    ...
    'corsheaders',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    ...
]

CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
]
```

### Redis (לפרודקשן)

לפרודקשן, מומלץ להשתמש ב-Redis במקום InMemoryChannelLayer:

1. התקן Redis
2. עדכן את `settings.py`:
```python
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [('127.0.0.1', 6379)],
        },
    },
}
```

## פתרון בעיות

### WebSocket לא מתחבר

1. ודא שהשרת רץ עם Daphne ולא עם runserver
2. בדוק שהפורט 8000 פתוח
3. בדוק את הקונסול בדפדפן לשגיאות

### הודעות לא נשלחות

1. ודא שאתה מחובר (בדוק את אינדיקטור החיבור)
2. ודא שאתה מחובר למערכת (authenticated)
3. בדוק את הקונסול של השרת לשגיאות

### CORS errors

הוסף את `django-cors-headers` והגדר את `CORS_ALLOWED_ORIGINS` ב-`settings.py`.

