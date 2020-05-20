import os

try:
    TOKEN = os.environ['STOKEN']
    MONGO_ADDRESS = os.environ.get("MONGO_ADDRESS")
    DB_NAME = os.environ.get("DB_NAME")
except KeyError:
    from bin_folder.secret import a, b, c
    TOKEN = a
    MONGO_ADDRESS = b
    DB_NAME = c