# mobile-service/Dockerfile
FROM python:3.12-slim

RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["sh", "-c", "while ! python -c \"import psycopg2; psycopg2.connect(host='mobile-db', user='mobile_user', password='mobile_pass', dbname='mobile_db')\" 2>/dev/null; do echo 'Waiting for DB...'; sleep 2; done && python manage.py makemigrations app && python manage.py migrate --noinput && gunicorn mobile_service.wsgi:application --bind 0.0.0.0:8006 --workers 2"]