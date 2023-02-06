FROM docker.io/python:3.11-slim

COPY requirements.txt /bot/requirements.txt

RUN pip install --no-cache-dir -r /bot/requirements.txt

COPY . /bot
