FROM python:3.13.2-slim

WORKDIR /app

# Устанавливаем системные зависимости для cryptography
RUN apt-get update && \
    apt-get install -y gcc python3-dev libssl-dev && \
    rm -rf /var/lib/apt/lists/*

# Копируем файлы проекта в контейнер
COPY . /app

# Устанавливаем зависимости
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir cryptography && \
    pip install --no-cache-dir -r requirements.txt

EXPOSE 5000

CMD ["python", "main.py"]