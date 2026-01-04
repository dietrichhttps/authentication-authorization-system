# Система аутентификации и авторизации

Собственная система аутентификации и авторизации на Django REST Framework с использованием PostgreSQL.

## Описание

Это приложение реализует полную систему управления пользователями и контроля доступа к ресурсам. Система не использует стандартные возможности Django из коробки, а реализует собственные механизмы аутентификации (JWT токены и сессии) и авторизации (на основе ролей и правил доступа).

## Основные возможности

### 1. Взаимодействие с пользователем
- **Регистрация**: Создание нового аккаунта (email, пароль, ФИО)
- **Вход в систему**: Авторизация по email и паролю
- **Выход из системы**: Завершение сессии пользователя
- **Обновление профиля**: Редактирование данных пользователя
- **Мягкое удаление аккаунта**: Деактивация аккаунта (is_active=False)

### 2. Система разграничения прав доступа
- Гибкая система ролей и правил доступа
- Контроль доступа к бизнес-объектам
- Разграничение прав на чтение, создание, обновление и удаление
- Различие между доступом к собственным объектам и ко всем объектам
- API для управления правилами доступа (для администраторов)

### 3. Mock бизнес-объекты
- Продукты (products)
- Заказы (orders)
- Магазины (shops)

## Схема базы данных

### Таблица `users` (Пользователи)
Хранит информацию о пользователях системы.

| Поле | Тип | Описание |
|------|-----|----------|
| id | Integer (PK) | Уникальный идентификатор |
| email | Email | Email пользователя (уникальный) |
| password_hash | Char(255) | Хеш пароля (bcrypt) |
| first_name | Char(100) | Имя |
| last_name | Char(100) | Фамилия |
| middle_name | Char(100) | Отчество |
| is_active | Boolean | Активен ли аккаунт |
| is_staff | Boolean | Является ли сотрудником |
| is_superuser | Boolean | Является ли суперпользователем |
| role_id | Integer (FK) | Ссылка на роль пользователя |
| date_joined | DateTime | Дата регистрации |
| updated_at | DateTime | Дата последнего обновления |

### Таблица `user_sessions` (Сессии пользователей)
Хранит активные сессии пользователей.

| Поле | Тип | Описание |
|------|-----|----------|
| id | Integer (PK) | Уникальный идентификатор |
| user_id | Integer (FK) | Ссылка на пользователя |
| session_token | Char(255) | Токен сессии (уникальный) |
| expires_at | DateTime | Время истечения сессии |
| created_at | DateTime | Дата создания |
| last_activity | DateTime | Последняя активность |

### Таблица `roles` (Роли)
Хранит роли пользователей в системе.

| Поле | Тип | Описание |
|------|-----|----------|
| id | Integer (PK) | Уникальный идентификатор |
| name | Char(100) | Название роли (уникальное) |
| description | Text | Описание роли |
| created_at | DateTime | Дата создания |
| updated_at | DateTime | Дата обновления |

**Примеры ролей:**
- `admin` - Администратор (полный доступ)
- `manager` - Менеджер (расширенные права)
- `user` - Обычный пользователь (базовые права)
- `guest` - Гость (ограниченные права)

### Таблица `business_elements` (Бизнес-элементы)
Описывает объекты бизнес-приложения, к которым осуществляется доступ.

| Поле | Тип | Описание |
|------|-----|----------|
| id | Integer (PK) | Уникальный идентификатор |
| name | Char(100) | Название элемента (уникальное) |
| description | Text | Описание элемента |
| created_at | DateTime | Дата создания |
| updated_at | DateTime | Дата обновления |

**Примеры элементов:**
- `products` - Продукты
- `orders` - Заказы
- `shops` - Магазины
- `users` - Пользователи
- `access_rules` - Правила доступа

### Таблица `access_roles_rules` (Правила доступа)
Связывает роли с бизнес-элементами и определяет права доступа.

| Поле | Тип | Описание |
|------|-----|----------|
| id | Integer (PK) | Уникальный идентификатор |
| role_id | Integer (FK) | Ссылка на роль |
| element_id | Integer (FK) | Ссылка на бизнес-элемент |
| read_permission | Boolean | Чтение своих объектов |
| read_all_permission | Boolean | Чтение всех объектов |
| create_permission | Boolean | Создание объектов |
| update_permission | Boolean | Обновление своих объектов |
| update_all_permission | Boolean | Обновление всех объектов |
| delete_permission | Boolean | Удаление своих объектов |
| delete_all_permission | Boolean | Удаление всех объектов |
| created_at | DateTime | Дата создания |
| updated_at | DateTime | Дата обновления |

**Уникальный ключ:** (role_id, element_id)

## Логика работы системы доступа

### Типы разрешений

1. **read_permission** - Пользователь может читать только свои объекты (где owner_id = user.id)
2. **read_all_permission** - Пользователь может читать все объекты
3. **create_permission** - Пользователь может создавать новые объекты
4. **update_permission** - Пользователь может обновлять только свои объекты
5. **update_all_permission** - Пользователь может обновлять все объекты
6. **delete_permission** - Пользователь может удалять только свои объекты
7. **delete_all_permission** - Пользователь может удалять все объекты

### Правила проверки

1. Если пользователь - суперпользователь (is_superuser=True), он имеет доступ ко всем ресурсам
2. Если у пользователя нет роли, доступ запрещен (403)
3. Проверяется наличие правила доступа для комбинации (роль, элемент)
4. Если нет конкретного разрешения (например, read_permission), проверяется всеобщее разрешение (read_all_permission)
5. При обновлении/удалении объекта проверяется владелец объекта, если нет всеобщего разрешения

### Коды ошибок

- **401 Unauthorized** - Пользователь не аутентифицирован
- **403 Forbidden** - Пользователь аутентифицирован, но не имеет доступа к ресурсу
- **404 Not Found** - Ресурс не найден

## Установка и настройка

### Требования

Для Docker (рекомендуется):
- Docker 20.10+
- Docker Compose 2.0+

Для локальной установки:
- Python 3.8+
- PostgreSQL 12+
- pip

## Установка через Docker (рекомендуется)

Самый простой способ запустить проект - использовать Docker Compose:

1. Клонируйте репозиторий:
```bash
git clone https://github.com/dietrichhttps/authentication-authorization-system.git
cd authentication-authorization-system
```

2. Запустите проект через Docker Compose:
```bash
docker-compose up --build
```

Эта команда автоматически:
- Создаст и запустит контейнер с PostgreSQL
- Соберет и запустит контейнер с Django приложением
- Применит миграции
- Загрузит тестовые данные
- Запустит сервер на `http://localhost:8000`

3. Приложение будет доступно по адресу: `http://localhost:8000`

### Работа с Docker

Остановить контейнеры:
```bash
docker-compose down
```

Остановить и удалить volumes (очистить базу данных):
```bash
docker-compose down -v
```

Просмотреть логи:
```bash
docker-compose logs -f
```

Выполнить команду в контейнере:
```bash
docker-compose exec web python manage.py createsuperuser
```

## Локальная установка

1. Клонируйте репозиторий или скопируйте файлы проекта

2. Создайте виртуальное окружение:
```bash
python3 -m venv venv
source venv/bin/activate  # На Windows: venv\Scripts\activate
```

3. Установите зависимости:
```bash
pip install -r requirements.txt
```

4. Создайте базу данных PostgreSQL и настройте пользователя:
```sql
-- Создайте базу данных
CREATE DATABASE auth_system;

-- Создайте роль пользователя (если нужно)
CREATE ROLE your_username WITH LOGIN CREATEDB PASSWORD 'your_password';

-- Или используйте существующего пользователя (например, postgres)
```

5. Настройте переменные окружения (создайте файл `.env` в корне проекта):
```
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-key-here
DB_NAME=auth_system
DB_USER=your_username
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432
```

**Важно:** Если вы используете пользователя отличного от `postgres`, убедитесь что у него есть права на создание таблиц в схеме `public`:
```sql
GRANT ALL PRIVILEGES ON SCHEMA public TO your_username;
GRANT ALL PRIVILEGES ON DATABASE auth_system TO your_username;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO your_username;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO your_username;
```

6. Примените миграции:
```bash
python manage.py makemigrations
python manage.py migrate
```

7. Загрузите тестовые данные:
```bash
python manage.py load_test_data
```

Эта команда создаст:
- Роли: admin, manager, user, guest
- Бизнес-элементы: products, orders, shops, users, access_rules
- Правила доступа для каждой роли
- Тестовых пользователей (см. ниже)

### Тестовые пользователи

После загрузки тестовых данных доступны следующие пользователи:

| Email | Пароль | Роль | Описание |
|-------|--------|------|----------|
| admin@example.com | admin123 | admin | Полный доступ ко всем ресурсам |
| manager@example.com | manager123 | manager | Расширенные права на продукты и заказы |
| user@example.com | user123 | user | Базовые права (только свои объекты) |
| guest@example.com | guest123 | guest | Только чтение продуктов и магазинов |

8. Создайте суперпользователя (опционально):
```bash
python manage.py createsuperuser
```

9. Запустите сервер разработки:
```bash
python manage.py runserver
```

## API Endpoints

### Аутентификация (`/api/auth/`)

- `POST /api/auth/register/` - Регистрация нового пользователя
- `POST /api/auth/login/` - Вход в систему
- `POST /api/auth/logout/` - Выход из системы
- `GET /api/auth/profile/` - Получение профиля текущего пользователя
- `PUT/PATCH /api/auth/profile/update/` - Обновление профиля
- `DELETE /api/auth/profile/delete/` - Мягкое удаление аккаунта

### Управление правами доступа (`/api/permissions/`) - Только для администраторов

- `GET /api/permissions/roles/` - Список всех ролей
- `GET /api/permissions/business-elements/` - Список всех бизнес-элементов
- `GET /api/permissions/access-rules/` - Список всех правил доступа
- `POST /api/permissions/access-rules/create/` - Создание нового правила
- `GET /api/permissions/access-rules/<id>/` - Получение правила по ID
- `PUT/PATCH /api/permissions/access-rules/<id>/update/` - Обновление правила
- `DELETE /api/permissions/access-rules/<id>/delete/` - Удаление правила

### Бизнес-объекты (`/api/business/`) - Требуется авторизация

**Продукты:**
- `GET /api/business/products/` - Список продуктов
- `GET /api/business/products/<id>/` - Получение продукта
- `POST /api/business/products/create/` - Создание продукта
- `PUT/PATCH /api/business/products/<id>/update/` - Обновление продукта
- `DELETE /api/business/products/<id>/delete/` - Удаление продукта

**Заказы:**
- `GET /api/business/orders/` - Список заказов
- `GET /api/business/orders/<id>/` - Получение заказа

**Магазины:**
- `GET /api/business/shops/` - Список магазинов

## Использование API

### Пример регистрации:

**Важно:** Все поля (first_name, last_name, middle_name) обязательны для заполнения.

```bash
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "password123",
    "password_confirm": "password123",
    "first_name": "Иван",
    "last_name": "Иванов",
    "middle_name": "Иванович"
  }'
```

### Пример входа:

```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "user123"
  }'
```

Ответ содержит JWT токен, который можно использовать для последующих запросов, а также устанавливает cookie с `session_id`.

### Пример запроса с токеном:

```bash
curl -X GET http://localhost:8000/api/auth/profile/ \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

Или с использованием cookie (автоматически устанавливается при login/register):
```bash
curl -X GET http://localhost:8000/api/auth/profile/ \
  -H "Cookie: session_id=YOUR_SESSION_TOKEN"
```

### Пример получения списка продуктов:

```bash
curl -X GET http://localhost:8000/api/business/products/ \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### Пример управления правилами доступа (только для администратора):

```bash
# Получить все правила доступа
curl -X GET http://localhost:8000/api/permissions/access-rules/ \
  -H "Authorization: Bearer ADMIN_JWT_TOKEN"

# Создать новое правило
curl -X POST http://localhost:8000/api/permissions/access-rules/create/ \
  -H "Authorization: Bearer ADMIN_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "role": 2,
    "element": 1,
    "read_permission": true,
    "create_permission": true
  }'
```

## Аутентификация

Система поддерживает два способа аутентификации:

1. **JWT токены** - Передается в заголовке `Authorization: Bearer <token>`
2. **Сессии** - Передается в cookie `session_id`

При успешном входе или регистрации система:
- Генерирует JWT токен (действителен 7 дней)
- Создает сессию в базе данных
- Устанавливает cookie с session_id

При выходе система удаляет сессию из базы данных и очищает cookie.

## Технологии

- **Django** 4.2.7 - Web-фреймворк
- **Django REST Framework** 3.14.0 - API фреймворк
- **PostgreSQL** - База данных
- **bcrypt** 4.1.1 - Хеширование паролей
- **PyJWT** 2.8.0 - Работа с JWT токенами
- **python-decouple** - Управление переменными окружения

## Структура проекта

```
authentication-authorization-system/
├── auth_system/          # Основные настройки проекта
├── users/                # Приложение пользователей
│   ├── models.py         # Модели User, Session
│   ├── views.py          # API для аутентификации
│   ├── serializers.py    # Сериализаторы
│   ├── utils.py          # Утилиты (JWT, сессии)
│   └── middleware.py     # Middleware для идентификации пользователя
├── permissions/          # Приложение управления правами
│   ├── models.py         # Модели Role, BusinessElement, AccessRoleRule
│   ├── views.py          # API для управления правами
│   ├── serializers.py    # Сериализаторы
│   └── utils.py          # Утилиты проверки прав
├── business/             # Приложение бизнес-объектов (Mock)
│   ├── views.py          # Mock-views для демонстрации
│   └── urls.py           # URL маршруты
├── Dockerfile            # Docker образ для приложения
├── docker-compose.yml    # Docker Compose конфигурация
├── docker-entrypoint.sh  # Скрипт инициализации для Docker
└── requirements.txt      # Зависимости Python
```
