import flask as fl
from threading import Thread

web = fl.Flask(__name__)

@web.route("/")
def mainmenu():
    return '<h1>Web server is working, and bot is online!</h1>'

def run():
    web.run(host="0.0.0.0", port=8080)

def run_web():
    t = Thread(target = run)
    t.start()