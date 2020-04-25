from flask import Flask
import main as m

app = Flask(__name__)

@app.route("/")
def run():
    return "Hello World"