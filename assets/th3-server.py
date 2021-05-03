import os
import sys
import time
from datetime import datetime
from functools import wraps
from typing import Any, Dict, Callable, Union, List

import redis
from bottle import request, response, Bottle

__version__ = "0.0.1"

TRANSLATIONS = {
    "Victory or Death": "Lok'Tar Ogar",
    "Lol": "Kek",
    "Okay": "Zug Zug",
    "Hey": "Es",
    "I obey": "Dabu",
    "By my Axe": "Gol'Kosh",
    "Well Met": "Throm-Ka"
}


def timing_and_logger(fn) -> Callable[..., Any]:
    """ Decorator function to log HTTP requests and timing info
    """

    @wraps(fn)
    def _timing_and_logger(*args, **kwargs) -> Dict:
        request_time: datetime = datetime.now()

        start: time.time = time.monotonic()
        actual_response: Dict = fn(*args, **kwargs)
        duration: time.time = time.monotonic() - start

        print(
            f"[{request_time}] {request.remote_addr} - {request.method} {request.fullpath}?{request.query_string} {response.status_code} - {duration * 1000:0.2f}ms")
        return actual_response

    return _timing_and_logger


def record_request_stats():
    """ Records stats for an http request in Redis
    """
    try:
        app.config['translateapp.redis'].hincrby("requests_by_ip", request.remote_addr, 1)
    except redis.RedisError as redis_err:
        print(f"Error sending stats to Redis: {redis_err}")


app: Bottle = Bottle()
app.install(timing_and_logger)


@app.route('/api/v1/translate')
def translate() -> Dict[str, Union[str, List[str]]]:
    """ Translate a phrase from Orcish to English
    """
    phrase: str = request.query.phrase or None
    response_body: Dict[str, Union[str, List[str]]] = {"phrase": phrase, "translation": None, "errors": []}

    if app.config.get('translateapp.redis'):
        record_request_stats()

    if not phrase:
        response.status = 400
        response_body['errors'].append("Missing phrase parameter")
        return response_body

    translation: str = TRANSLATIONS.get(phrase)

    if not translation:
        response.status = 404
        response_body['errors'].append("Translation not available")
        return response_body

    response_body['translation'] = translation
    return response_body


@app.route('/version')
def version() -> Dict[str, Union[str, List[str]]]:
    """ Return the app version
    """
    return {"version": __version__, "errors": []}


if __name__ == '__main__':
    redis_addr: str = os.getenv("REDIS_ADDR")
    if redis_addr:
        try:
            app.config['translateapp.redis']: redis.Redis = redis.Redis(host=redis_addr, port=6379, db=0)
            # Run a command to make sure redis connection info is correct
            app.config['translateapp.redis'].info()
        except redis.RedisError as redis_err:
            print(f"Error connecting to Redis: {redis_err}")
            sys.exit(1)

    app.run(host='0.0.0.0', port=8080, server='gunicorn', workers=4)