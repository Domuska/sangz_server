from werkzeug.serving import run_simple
from werkzeug.wsgi import DispatcherMiddleware
from jukebox.resources import app as jukebox
from client.application import app as client

application = DispatcherMiddleware(jukebox, {
    '/sangz/client': client
})
if __name__ == '__main__':
    run_simple('localhost', 5000, application,
               use_reloader=True, use_debugger=True, use_evalex=True)