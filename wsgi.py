import logging

from fjfnaranjobot.bot import Bot


logging.basicConfig(level=logging.INFO)

bot = Bot()
#bot.start_webhook()


def application(environ, start_response):
    """Simplest possible application object"""
    data = 'Hello, World!\n'
    status = '200 OK'
    response_headers = [
        ('Content-type','text/plain'),
        ('Content-Length', str(len(data)))
    ]
    start_response(status, response_headers)
    return iter([data])
