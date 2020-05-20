FROM python:3.8.3-alpine

COPY . /bot

RUN apk add --no-cache \
		gcc \
		python3-dev \
		musl \
		musl-dev \
		libffi \
		libffi-dev \
		openssl \
		openssl-dev \
		uwsgi-python3 \
	&& pip3 install --no-cache-dir -r /bot/requirements.txt \
	&& apk del \
		python3-dev \
		musl-dev \
		libffi-dev \
		openssl-dev \
	&& rm /bot/requirements.txt
