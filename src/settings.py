from os import environ

DB_URL = environ.get("DB_URL", "mongodb://localhost:27017/polls")
