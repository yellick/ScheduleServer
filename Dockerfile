FROM python:3.13.2-slim

WORKDIR /app

# Устанавливаем минимальные зависимости с очисткой кэша
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc python3-dev libffi-dev libssl-dev && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Сначала копируем только requirements.txt
COPY requirements.txt .

# Устанавливаем зависимости с оптимизациями
RUN python -m pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir \
    --no-build-isolation \
    --only-binary=:all: \
    -r requirements.txt

# Копируем остальные файлы
COPY . .

EXPOSE 5000
CMD ["python", "main.py"]