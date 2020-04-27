from flask import Flask
from threading import Thread
import main

app = Flask(__name__)

@app.route("/")
def run():
    main.botrun()
    return "<h1>Hello World<h2>"