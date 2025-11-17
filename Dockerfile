FROM python:3.12-slim

WORKDIR /backend

COPY pyproject.toml ./

RUN pip install --upgrade pip setuptools wheel \
    && pip install .

COPY . .

EXPOSE 8000

CMD ["bash", "-c", "python3 manage.py makemigrations && python3 manage.py migrate && python3 manage.py collectstatic --noinput && gunicorn settings.wsgi:application --bind 0.0.0.0:8000"]
