FROM python:3.12
LABEL authors="Yaron"

WORKDIR /app

COPY .. /app

RUN pip install --no-cache-dir -r /app/requirements.txt

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]