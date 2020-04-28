from flask import Flask

app = Flask(__name__)

@app.route("/")
def run():
    Thread(target=main.botrun()).start()
    return "<h1>Hello World<h2>"