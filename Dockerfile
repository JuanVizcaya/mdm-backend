FROM python:3.7

ENV PYTHONUNBUFFERED 1

RUN mkdir /app

COPY . /app/

WORKDIR /app

RUN apt-get update &&\
    apt-get install -y binutils libproj-dev gdal-bin

RUN pip install --upgrade pip \
    && pip install -r requirements.txt
