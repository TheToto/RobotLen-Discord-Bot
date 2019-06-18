from bottle import route, run
import settings


@route('/')
def index():
    return "Hello"


def launch_server():
    run(host='localhost', port=settings.WEB_PORT)
