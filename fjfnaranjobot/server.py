from collections import namedtuple
from warnings import filterwarnings

from telegram.warnings import PTBUserWarning

from fjfnaranjobot.bot import BotJSONError, BotTokenError, ensure_bot
from fjfnaranjobot.logging import getLogger

filterwarnings(
    action="ignore", message=r".*CallbackQueryHandler", category=PTBUserWarning
)

logger = getLogger(__name__)

bot = ensure_bot()


async def application(scope, receive, send):
    assert scope["type"] == "http"

    async def send_text_response(text, status=200):
        await send(
            {
                "type": "http.response.start",
                "status": status,
                "headers": [
                    [b"content-type", b"text/plain"],
                ],
            }
        )
        await send(
            {
                "type": "http.response.body",
                "body": bytes(text, "utf8"),
            }
        )

    async def read_body():
        body = b""
        more_body = True

        while more_body:
            message = await receive()
            body += message.get("body", b"")
            more_body = message.get("more_body", False)

        return body

    try:
        logger.debug("Defer request to bot for processing.")
        request_body = await read_body()
        bot_reply = await bot.process_request(scope["path"], request_body)
        await send_text_response(bot_reply)
    except BotJSONError as e:
        logger.info("Error from bot framework (json).", exc_info=e)
        await send_text_response(str(e), status=400)
    except BotTokenError as e:
        logger.info("Error from bot framework (token).", exc_info=e)
        await send_text_response("404 Not Found", status=404)
    except Exception as e:
        logger.exception("Error from bot framework or library.", exc_info=e)
        await send_text_response(str(e), status=500)
