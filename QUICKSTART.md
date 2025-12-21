# Быстрый старт

## Шаг 1: Установка зависимостей

```bash
# Создайте виртуальное окружение (если еще не создано)
python3 -m venv venv
source venv/bin/activate  # На Windows: venv\Scripts\activate

# Установите зависимости
pip install -r requirements.txt
```

## Шаг 2: Настройка базы данных

```bash
# Создайте базу данных PostgreSQL
createdb auth_system

# Или через psql:
psql -U postgres
CREATE DATABASE auth_system;
\q
```

## Шаг 3: Настройка переменных окружения

Создайте файл `.env` в корне проекта (можно скопировать из `.env.example` если есть):

```env
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-key-here
DB_NAME=auth_system
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=localhost
DB_PORT=5432
```

## Шаг 4: Применение миграций

```bash
python manage.py migrate
```

## Шаг 5: Загрузка тестовых данных

```bash
python manage.py load_test_data
```

Это создаст:
- Роли: admin, manager, user, guest
- Бизнес-элементы: products, orders, shops, users, access_rules
- Правила доступа для каждой роли
- Тестовых пользователей

## Шаг 6: Запуск сервера

```bash
python manage.py runserver
```

## Тестовые пользователи

После загрузки тестовых данных доступны следующие пользователи:

| Email | Пароль | Роль | Описание |
|-------|--------|------|----------|
| admin@example.com | admin123 | admin | Полный доступ ко всем ресурсам |
| manager@example.com | manager123 | manager | Расширенные права на продукты и заказы |
| user@example.com | user123 | user | Базовые права (только свои объекты) |
| guest@example.com | guest123 | guest | Только чтение продуктов и магазинов |

## Примеры использования API

### Регистрация

```bash
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "password123",
    "password_confirm": "password123",
    "first_name": "Test",
    "last_name": "User"
  }'
```

### Вход в систему

```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "user123"
  }'
```

Ответ содержит токен, который можно использовать для последующих запросов.

### Получение профиля (с токеном)

```bash
curl -X GET http://localhost:8000/api/auth/profile/ \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### Получение списка продуктов

```bash
curl -X GET http://localhost:8000/api/business/products/ \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### Управление правилами доступа (только для администратора)

```bash
# Получить все правила
curl -X GET http://localhost:8000/api/permissions/access-rules/ \
  -H "Authorization: Bearer ADMIN_JWT_TOKEN"
```

## Проверка работы системы

1. Войдите как обычный пользователь (user@example.com)
2. Попробуйте получить список продуктов - должны увидеть только свои продукты
3. Войдите как менеджер (manager@example.com)
4. Попробуйте получить список продуктов - должны увидеть все продукты
5. Войдите как администратор (admin@example.com)
6. Попробуйте управлять правилами доступа через API

