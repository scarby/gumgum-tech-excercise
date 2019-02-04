FROM python:3.7.2-alpine3.8

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["gunicorn"  , "-b", "0.0.0.0:8000", "cache:app"]