import urllib.parse

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.core.config import Config

connection_string = (
    f"DRIVER={Config.DB_DRIVER};"
    f"SERVER={Config.DB_SERVER};"
    f"DATABASE={Config.DB_NAME};"
    f"UID={Config.DB_USER};"
    f"PWD={Config.DB_PASSWORD};"
    "Encrypt=yes;"
    "TrustServerCertificate=no;"
)

params = urllib.parse.quote_plus(connection_string)

engine = create_engine(f"mssql+pyodbc:///?odbc_connect={params}", pool_size=10)

SessionLocal = sessionmaker(engine)


def get_db():
    with SessionLocal() as session:
        yield session
