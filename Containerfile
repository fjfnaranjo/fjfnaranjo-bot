FROM docker.io/python:3.11-slim
WORKDIR /bot
COPY requirements.txt .
COPY fjfnaranjobot fjfnaranjobot
RUN python3 -m venv /venv \
	&& /venv/bin/pip install --no-cache-dir -r /bot/requirements.txt
ENTRYPOINT ["/venv/bin/python3", "-m", "fjfnaranjobot.server"]
