# Attempt at Dockerfile for heroku but couldn't even test it locally
# as I didn't get the docker django instance to connect successfully
# with postgresql server running on host

FROM python:3.8-alpine

WORKDIR /app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV DEBUG 0

# install psycopg2
RUN apk update \
    && apk add --virtual build-deps gcc python3-dev musl-dev \
    && apk add postgresql-dev \
    && pip install psycopg2 \
    && apk del build-deps

# install dependencies
ADD requirements.txt /app/requirements.txt
RUN pip install -r requirements.txt

# install dependencies
ADD . /app

#RUN adduser -D appuser
#USER appuser

CMD gunicorn readlater_django.wsgi:application --bind 0.0.0.0:$PORT

EXPOSE 8000
