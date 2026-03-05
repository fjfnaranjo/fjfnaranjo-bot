# fjfnaranjo-bot

A simple Telegram bot written in Python.

![fjfnaranjo-bot](https://github.com/fjfnaranjo/fjfnaranjo-bot/workflows/fjfnaranjo-bot/badge.svg)

## Development

```sh
# Copy the config templates and fill them
cp environment .env
cp botdata/nginx.conf.example botdata/nginx.conf

# Create the dev image
make build-dev

# Sort imports
make isort

# Black the code
make black

# Run the tests
make test
```

## Running the bot locally

```sh
# Create a self-signed certificate for local hosting
openssl req -newkey rsa:2048 -sha256 -nodes -keyout botdata/nginx/certs/YOURDOMAIN.EXAMPLE.key -x509 -days 365 -out botdata/nginx/certs/YOURDOMAIN.EXAMPLE.pem -subj "/C=US/ST=New York/L=Brooklyn/O=Example Brooklyn Company/CN=YOURDOMAIN.EXAMPLE"

# Review the env and nginx configuration

# Run the bot
podman-compose up -d

# Call the register webhook endpoint for self-signed certificates
curl https://YOURDOMAIN.EXAMPLE:8443/WEBHOOK_TOKEN/register_webhook_self
```
