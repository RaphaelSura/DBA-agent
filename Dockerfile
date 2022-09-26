# syntax=docker/dockerfile:1

FROM arm32v7/python:3.8-buster

RUN pip3 install --upgrade pip setuptools wheel

RUN mkdir /app
WORKDIR /app

COPY requirements.txt ./
RUN pip3 install -r requirements.txt

COPY . .

RUN pip3 install -e /app


CMD [ "python3", "src/dbagent/app.py"]