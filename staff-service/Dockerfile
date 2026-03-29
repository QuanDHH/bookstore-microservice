# staff-service/Dockerfile
FROM python:3.12-slim
 
# Install MySQL client libs (needed by mysqlclient)
RUN apt-get update && apt-get install -y \
    gcc \
    default-libmysqlclient-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*
 
WORKDIR /app
 
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
 
COPY . .
 
# Run migrations then start Gunicorn on port 8001
CMD ["sh", "-c", "python manage.py migrate --noinput && gunicorn staff_service.wsgi:application --bind 0.0.0.0:8001 --workers 2"]
 
