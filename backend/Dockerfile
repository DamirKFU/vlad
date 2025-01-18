# Используем официальный образ Python
FROM python:3.9

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем requirements.txt и устанавливаем зависимости
COPY requirements/prod.txt .
RUN pip install --no-cache-dir -r prod.txt

# Копируем все файлы приложения
COPY . .

# Собираем статические файлы
RUN python manage.py collectstatic --noinput

# Открываем порт 8000
EXPOSE 8000

# Запускаем Django приложение
CMD ["sh", "-c", "cd /app/backend && python manage.py migrate && python manage.py init_admin && python manage.py init_admin && gunicorn -w 3 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000 backend.asgi:application --reload"]
