#!/bin/bash
set -e

# Ждем готовности базы данных
echo "Waiting for database..."
while ! pg_isready -h "$DB_HOST" -U "$DB_USER" -p "$DB_PORT" > /dev/null 2>&1; do
  sleep 1
done

echo "Database is ready!"

# Применяем миграции
echo "Running migrations..."
python manage.py migrate --noinput

# Загружаем тестовые данные (если они еще не загружены)
echo "Loading test data..."
python manage.py load_test_data || echo "Test data already loaded or error occurred"

# Запускаем команду
exec "$@"
