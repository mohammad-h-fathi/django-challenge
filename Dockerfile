FROM python:3.9-alpine as builder

WORKDIR /usr/src/app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1


RUN apk update
RUN apk add --virtual build-deps gcc python3-dev musl-dev
RUN apk add --no-cache mariadb-dev

COPY ./requirements.txt .
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /usr/src/app/wheels -r requirements.txt

RUN apk del build-deps

FROM python:3.9-alpine

RUN mkdir -p /home/app

# create the app user
RUN adduser -S -D  -u 1002 app

# create the appropriate directories
ENV HOME=/home/app
ENV APP_HOME=/home/app/web
RUN mkdir $APP_HOME
RUN mkdir $APP_HOME/static
RUN mkdir $APP_HOME/media

WORKDIR $APP_HOME


# install dependencies
RUN apk update
RUN apk add --virtual build-deps gcc python3-dev musl-dev
RUN apk add --no-cache mariadb-dev

COPY --from=builder /usr/src/app/wheels /wheels
COPY --from=builder /usr/src/app/requirements.txt .
RUN pip install --no-cache /wheels/*

RUN apk del build-deps

# copy project
COPY . $APP_HOME

# chown all the files to the app user
RUN chown -R app $APP_HOME
RUN chmod +x entrypoint.sh
# change to the app user
USER app
EXPOSE 8000
CMD ["python", "manage.py", "collectstatic", "-noinput"]
CMD ["gunicorn", "TicketReservation.wsgi", "--bind", "0.0.0.0:8000", "--workers", "2"]