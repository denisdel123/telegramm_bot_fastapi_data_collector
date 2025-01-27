import os

from dotenv import load_dotenv

load_dotenv()

POSTGRES_PASSWORD = os.environ.get("POSTGRES_PASSWORD")
POSTGRES_BD = os.environ.get("POSTGRES_BD")
POSTGRES_USER = os.environ.get("POSTGRES_USER")
POSTGRES_PORT = os.environ.get("POSTGRES_PORT")
POSTGRES_HOST = os.environ.get("POSTGRES_HOST")
