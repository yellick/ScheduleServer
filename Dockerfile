FROM python:3.13.2-slim

WORKDIR /app

# Устанавливаем только минимальные зависимости
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc python3-dev libffi-dev libssl-dev && \
    rm -rf /var/lib/apt/lists/*

# Сначала копируем только requirements.txt
COPY requirements.txt .

# Устанавливаем зависимости с оптимизациями
RUN pip install --no-cache-dir --upgrade pip==24.0.2 && \
    pip install --no-cache-dir \
    --no-build-isolation \
    --only-binary=:all: \
    -r requirements.txt

# Копируем остальные файлы
COPY . .

EXPOSE 5000
CMD ["python", "main.py"]