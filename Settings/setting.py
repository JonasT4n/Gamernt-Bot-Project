import os
import psycopg2

DBPOSTGRE = os.environ['DATABASE_URL']
TOKEN = os.environ['STOKEN']
MONGO_ADDRESS = os.environ.get("MONGO_ADDRESS")
DB_NAME = os.environ.get("DB_NAME")

conn = psycopg2.connect(DBPOSTGRE, sslmode='require')