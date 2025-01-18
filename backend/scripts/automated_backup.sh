#!/bin/bash

# Загружаем переменные окружения из .env файла
if [ -f .env ]; then
    export $(cat .env | grep -v '#' | awk '/=/ {print $1}')
fi

# Включаем режим обслуживания
echo "Enabling maintenance mode..."
docker-compose exec -T django python manage.py shell -c "import os; os.environ['MAINTENANCE_MODE'] = 'true'"

# Ждем завершения текущих запросов (30 секунд)
sleep 30

# Создаем бэкап
echo "Creating backup..."
docker-compose exec -T backup /scripts/backup.sh

# Выключаем режим обслуживания
echo "Disabling maintenance mode..."
docker-compose exec -T django python manage.py shell -c "import os; os.environ['MAINTENANCE_MODE'] = 'false'"

echo "Backup process completed" 