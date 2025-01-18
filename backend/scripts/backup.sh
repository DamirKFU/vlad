#!/bin/bash
set -e

echo "[$(date)] Starting backup process..."
echo "[$(date)] Environment variables:"
echo "POSTGRES_HOST: $POSTGRES_HOST"
echo "POSTGRES_USER: $POSTGRES_USER"
echo "POSTGRES_DB: $POSTGRES_DB"
echo "Testing connection string: psql -h $POSTGRES_HOST -U $POSTGRES_USER -d $POSTGRES_DB"

# Текущая дата для имени файла
BACKUP_DATE=$(date +%Y-%m-%d_%H-%M-%S)
BACKUP_DIR="/backups"

# Создаем директорию для бэкапов если её нет
mkdir -p $BACKUP_DIR
chmod 777 $BACKUP_DIR

echo "[$(date)] Waiting for database..."
# Ждем доступности базы данных
export PGPASSWORD=$POSTGRES_PASSWORD
until psql -h "$POSTGRES_HOST" -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c '\l' > /dev/null 2>&1; do
  echo "[$(date)] Postgres is unavailable - sleeping"
  sleep 1
done

echo "[$(date)] Creating PostgreSQL backup..."
# Бэкап PostgreSQL
pg_dump -h "$POSTGRES_HOST" -U "$POSTGRES_USER" -d "$POSTGRES_DB" | gzip > "$BACKUP_DIR/db_$BACKUP_DATE.sql.gz"

echo "[$(date)] Creating media backup..."
# Бэкап медиа файлов
if [ -d "/app/media" ]; then
    tar -czf "$BACKUP_DIR/media_$BACKUP_DATE.tar.gz" -C /app/media .
else
    echo "[$(date)] Media directory not found, skipping media backup"
fi

# Проверяем создание файлов
echo "[$(date)] Checking created files:"
ls -la $BACKUP_DIR

# Удаляем бэкапы старше 7 дней
find $BACKUP_DIR -name "*.gz" -type f -mtime +7 -delete

echo "[$(date)] Backup completed successfully" 