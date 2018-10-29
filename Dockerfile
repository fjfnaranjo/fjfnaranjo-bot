FROM alpine:3.7

RUN apk add --no-cache \
	make \
	gcc \
	uwsgi-python3 \
	python3 \
	python3-dev \
	musl-dev \
	libffi-dev \
	openssl-dev

COPY requirements.txt /tmp/requirements.txt

RUN pip3 install --no-cache-dir -r /tmp/requirements.txt

RUN rm /tmp/requirements.txt

