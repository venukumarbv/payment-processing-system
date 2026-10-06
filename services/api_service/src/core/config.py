import os

from dotenv import load_dotenv

load_dotenv()


class Config:
    DB_SERVER = os.getenv("DB_SERVER")
    DB_NAME = os.getenv("DB_NAME")
    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    DB_DRIVER = os.getenv("DB_DRIVER")

    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "")  # TODO
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 30
