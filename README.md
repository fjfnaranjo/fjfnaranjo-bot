# fjfnaranjo-bot
A simple Telegram bot written in Python.

![fjfnaranjo-bot](https://github.com/fjfnaranjo/fjfnaranjo-bot/workflows/fjfnaranjo-bot/badge.svg)
# Notes
## Create a self-signed certificate
`openssl req -newkey rsa:2048 -sha256 -nodes -keyout YOURPRIVATE.key -x509 -days 365 -out YOURPUBLIC.pem -subj "/C=US/ST=New York/L=Brooklyn/O=Example Brooklyn Company/CN=YOURDOMAIN.EXAMPLE"`
