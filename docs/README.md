# KinoPoisk API/Frontend

## Stack
- Backend: Django + DRF, JWT (simplejwt), drf-spectacular, custom user (email login), custom permissions.
- Domain: Movies, comments (nested), ratings, likes (generic), reviews, favorites, video upload for movies.
- Frontend: React + Vite + TypeScript; REST client with axios.
- Infra: Docker Compose (postgres, backend, frontend), seed commands with Faker.

## How to run (Docker, рекомендовано)
1. Скопируй env (если нет): `cp env.example .env`
2. Запуск всего проекта: `./run.sh`
   - Поднимет Postgres, применит миграции, соберёт и запустит backend+frontend.
3. Остановить: `docker compose down`

## Локальный запуск (без Docker)
```bash
python -m venv venv && source venv/bin/activate
pip install -r backend/requirements.txt
export KINOPOISK_ENV_ID=local
cd backend
python manage.py migrate
python manage.py runserver
```
Фронт:
```bash
cd frontend
npm install
npm run dev
```

## Данные (seeding)
- Пользователи: `python manage.py generate_user_data`
- Полный набор фильмов/лайков/рейтингов/комментов: `python manage.py generate_movie_data`

## API
- Base URL: `/api/`
- Auth: `/api/auth/register/`, `/api/auth/login/`, `/api/auth/logout/`, `/api/auth/profile/`
- Movies: list/detail/search, rate, like/unlike, comments CRUD (частично), reviews CRUD, favorites, video upload (admin/staff) `/api/movies/<id>/video/`
- Документация: Swagger `/api/docs/`, Redoc `/api/redoc/`, схема `/api/schema/`

## Тесты
- Backend (в Docker): `docker compose run --rm backend-test`
- Локально: `cd backend && pytest`

## Права доступа
- JWT обязательны для защищённых ручек.
- Custom permissions: `IsStaffOrReadOnly`, `IsOwnerOrAdmin`, `IsSelfOrAdmin` применены к owner-only операциям (reviews/ratings/favorites и т.д.).

## Видео
- Админ загружает: `PUT/POST /api/movies/<movie_id>/video/` multipart с полем `video`.
- Фронт показывает плеер на детальной странице; форма загрузки видна только staff.
