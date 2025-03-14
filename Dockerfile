# Используем официальный образ Python 3.13.1
FROM python:3.13.2-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
build-essential \
python3-dev \
&& rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["uwsgi", "--http", "0.0.0.0:5000", "--module", "main:main"]