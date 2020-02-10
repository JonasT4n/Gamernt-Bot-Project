import flask as fl

web = fl.Flask(__name__)

@web.route("/")
def mainmenu():
    pass

def run():
    pass

if __name__ == '__main__':
    run()