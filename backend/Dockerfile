FROM python:3.10.11

WORKDIR /app

COPY requirements/prod.txt requirements.txt
COPY .env .env
RUN pip install -r requirements.txt

COPY . .

CMD ["gunicorn", "backend.wsgi:application", "--bind", "0.0.0.0:8000"]