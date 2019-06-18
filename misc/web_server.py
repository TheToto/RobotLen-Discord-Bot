from bottle import route, run
from misc import settings


@route('/')
def index():
    return "Hello"


def launch_web_server():
    print("Launch")
    run(host='0.0.0.0', port=settings.WEB_PORT)
