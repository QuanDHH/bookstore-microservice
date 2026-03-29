# customer-service/Dockerfile
FROM python:3.12-slim

RUN apt-get update && apt-get install -y \
    gcc \
    default-libmysqlclient-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["sh", "-c", "while ! python -c \"import MySQLdb; MySQLdb.connect(host='customer-db', user='customer_user', passwd='customer_pass', db='customer_db')\" 2>/dev/null; do echo 'Waiting for DB...'; sleep 2; done && python manage.py makemigrations app && python manage.py migrate --noinput && gunicorn customer_service.wsgi:application --bind 0.0.0.0:8002 --workers 2"]
