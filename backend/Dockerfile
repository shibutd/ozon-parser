FROM python:3.7-alpine

RUN apk update

# required for lxml
RUN apk add libxml2-dev libxslt-dev

# required for psycopg2
RUN apk add gcc musl-dev postgresql-dev

WORKDIR /backend

RUN pip install --upgrade pip

COPY ./requirements.txt /backend/
RUN pip install -r requirements.txt

COPY . /backend/
