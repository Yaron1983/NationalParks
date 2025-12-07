# הוראות הפעלה - מערכת חדרי צ'ט

## שלב 1: התקנת תלויות Backend

```bash
cd national_parks
pip install -r requirements.txt
```

## שלב 2: הכנת מסד הנתונים

```bash
python manage.py makemigrations chat
python manage.py migrate
```

## שלב 3: הפעלת Backend (Django + WebSockets)

**אפשרות 1: עם Daphne (מומלץ ל-WebSockets)**
```bash
daphne -b 0.0.0.0 -p 8000 national_parks.asgi:application
```

**אפשרות 2: עם runserver (לפיתוח בלבד)**
```bash
python manage.py runserver
```

השרת ירוץ על: http://localhost:8000

## שלב 4: התקנת תלויות Frontend

פתח טרמינל חדש:

```bash
cd chat_frontend
npm install
```

## שלב 5: הפעלת Frontend (React)

```bash
npm start
```

האפליקציה תרוץ על: http://localhost:3000

## גישה למערכת

1. **דף הצ'ט באתר Django**: http://localhost:8000/chat/
2. **אפליקציית React המלאה**: http://localhost:3000
3. **API Endpoints**: http://localhost:8000/api/chat/rooms/

## פתרון בעיות

### שגיאת "ModuleNotFoundError: No module named 'django'"
```bash
# ודא שאתה בסביבה וירטואלית
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate
pip install -r requirements.txt
```

### שגיאת "port already in use"
```bash
# שנה את הפורט ב-runserver:
python manage.py runserver 8001
```

### WebSocket לא עובד
- ודא שהשרת רץ עם `daphne` ולא עם `runserver`
- בדוק שהפורט 8000 פתוח

### CORS errors
- ודא ש-`django-cors-headers` מותקן
- ודא שהגדרות CORS ב-`settings.py` נכונות

## יצירת משתמש מנהל (אם צריך)

```bash
python manage.py createsuperuser
```

## בדיקה שהכל עובד

1. פתח http://localhost:8000/chat/ - צריך לראות את דף הצ'ט
2. פתח http://localhost:3000 - צריך לראות את אפליקציית React
3. לחץ על "צור חדר חדש" ונסה לשלוח הודעה

