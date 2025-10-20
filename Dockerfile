FROM python:3.11-slim

WORKDIR /app

# Cài dependency hệ thống (cho mysqlclient, confluent-kafka...)
RUN apt-get update && apt-get install -y \
    gcc \
    default-libmysqlclient-dev \
    librdkafka-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . .

# Default CMD có thể override trong docker-compose
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]