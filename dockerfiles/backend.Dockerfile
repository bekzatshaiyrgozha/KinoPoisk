FROM python:3.12-slim

WORKDIR /backend

RUN apt-get update && apt-get install -y curl

COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

COPY ../backend/pyproject.toml ./

RUN uv pip install --system --no-cache . \
    && rm -rf /root/.cache

COPY ../backend .

EXPOSE 8000

CMD ["sh", "-c", "python3 manage.py collectstatic --noinput && python3 manage.py migrate && python3 manage.py generate_movie_data && gunicorn settings.wsgi:application --bind 0.0.0.0:8000"]

HEALTHCHECK --interval=10s --timeout=2s --start-period=5s CMD curl -f http://localhost:8000/api/health/ || exit 1