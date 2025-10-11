FROM python:3.12-slim 
WORKDIR /app

COPY requirements.txt . 

RUN pip install -r requirements.txt 

EXPOSE 8000

COPY . .

CMD ["gunicorn", "settings.wsgi:application", "--bind", "0.0.0.0:8000"]