# KinoPoisk

Полнофункциональная платформа для фильмов: backend на Django REST Framework и frontend на React + TypeScript.

## Что внутри

- Backend API: аутентификация, фильмы, комментарии, лайки, рейтинги, отзывы, избранное
- Frontend SPA: просмотр фильмов, поиск, авторизация, работа с API
- Документация API через Swagger/ReDoc
- Docker-окружение (PostgreSQL + pgAdmin + backend + frontend)

## Технологии

### Backend
- Python 3.10+
- Django 5.2
- Django REST Framework
- SimpleJWT (JWT auth)
- drf-spectacular (OpenAPI/Swagger)
- PostgreSQL / SQLite
- Gunicorn, WhiteNoise

### Frontend
- React 19
- TypeScript
- Vite
- Tailwind CSS
- React Router
- Axios

## Структура проекта

- backend/ — Django API
- frontend/ — React-приложение
- docker-compose.yml — общий docker-стек
- env.example — пример переменных окружения
- docs/README.md — дополнительные заметки

## Быстрый старт

### 1) Клонирование и .env

Скопируйте пример переменных:

```bash
cp env.example .env
```

## Запуск через Docker (рекомендуется)

Из корня проекта:

```bash
docker compose up --build -d
```

Сервисы после запуска:

- Frontend: http://localhost
- Backend API: http://localhost:8000
- Swagger: http://localhost:8000/api/docs/
- ReDoc: http://localhost:8000/api/redoc/
- OpenAPI schema: http://localhost:8000/api/schema/
- pgAdmin: http://localhost:5050

Остановка:

```bash
docker compose down
```

С очисткой volumes:

```bash
docker compose down -v
```

## Локальный запуск без Docker

### Backend

Перейдите в backend:

```bash
cd backend
```

Установите зависимости (вариант 1 — uv):

```bash
uv sync
```

Или (вариант 2 — poetry/pip):

```bash
poetry install
```

Убедитесь, что в окружении задано:

- KINOPOISK_ENV_ID=local (для SQLite)
- либо KINOPOISK_ENV_ID=prod (для PostgreSQL)

Примените миграции:

```bash
python manage.py migrate
```

Создайте суперпользователя (опционально):

```bash
python manage.py createsuperuser
```

Запустите backend:

```bash
python manage.py runserver
```

Backend будет доступен на http://localhost:8000

### Frontend

В новом терминале:

```bash
cd frontend
npm install
npm run dev
```

Frontend dev-сервер: http://localhost:5173

## Переменные окружения

Минимально используемые переменные (см. env.example):

- KINOPOISK_ENV_ID — режим настроек (`local` или `prod`)
- POSTGRES_USER
- POSTGRES_PASSWORD
- POSTGRES_DB
- POSTGRESQL_URL
- PGADMIN_EMAIL
- PGADMIN_PASSWORD
- SECRET_KEY

Пример `POSTGRESQL_URL`:

```env
POSTGRESQL_URL=postgres://myuser:mypassword@postgres:5432/mydatabase
```

## Основные API-маршруты

Префикс: `/api`

### Auth
- `POST /api/auth/register/`
- `POST /api/auth/login/`
- `POST /api/auth/logout/`
- `GET|PUT|PATCH /api/auth/profile/`

### Movies
- `GET /api/movies/`
- `GET /api/movies/search/`
- `GET /api/movies/{id}/`
- `POST|PUT /api/movies/{id}/video/`
- `GET|POST /api/movies/{id}/comments/`
- `POST /api/movies/{id}/rate/`

### Extra entities
- `POST /api/movies/like/`
- `GET|POST /api/movies/reviews/`
- `GET|PATCH|DELETE /api/movies/reviews/{id}/`
- `GET|POST /api/movies/ratings/`
- `DELETE /api/movies/ratings/{id}/`
- `GET|POST /api/movies/favorites/`
- `DELETE /api/movies/favorites/{id}/`

## Полезные команды

### Backend

```bash
cd backend
python manage.py makemigrations
python manage.py migrate
python manage.py test
```

### Frontend

```bash
cd frontend
npm run dev
npm run build
npm run preview
npm run lint
```

## Частые проблемы

1. Ошибка настроек окружения
- Проверьте `KINOPOISK_ENV_ID` (`local` или `prod`).

2. Backend не подключается к БД в Docker
- Проверьте `POSTGRESQL_URL` в `.env` и состояние контейнера `postgres`.

3. CORS/доступ с фронтенда
- Для Docker и локальной разработки уже добавлены типовые origin (localhost).

## Лицензия

Смотрите файл лицензии в директории docs.
