from threading import Thread
from flask import Flask

app = Flask(__name__)

@app.route("/")
def run():
    return "<h1>Hello World<h2>"

def onrun():
    app.run(host="0.0.0.0", port=8080)

def forever():
    Thread(target=onrun()).start()