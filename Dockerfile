FROM python:3.13.2-slim

WORKDIR /app

# Копируем файлы проекта в контейнер
COPY . /app

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 5000

CMD ["uwsgi", "--http", "0.0.0.0:5000", "--module", "main:app"]