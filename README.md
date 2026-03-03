# fjfnaranjo-bot
A simple Telegram bot written in Python.

![fjfnaranjo-bot](https://github.com/fjfnaranjo/fjfnaranjo-bot/workflows/fjfnaranjo-bot/badge.svg)
## Development

```sh
# Copy the config templates and fill them
cp environment .env
cp botdata/nginx.conf.example botdata/nginx.conf

# Create a self-signed certificate for local hosting
openssl req -newkey rsa:2048 -sha256 -nodes -keyout botdata/certs/YOURDOMAIN.EXAMPLE.key -x509 -days 365 -out botdata/certs/YOURDOMAIN.EXAMPLE.pem -subj "/C=US/ST=New York/L=Brooklyn/O=Example Brooklyn Company/CN=YOURDOMAIN.EXAMPLE"
```
