import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    MYSQL_USER = os.getenv("MYSQL_USER")
    MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
    MYSQL_HOST = os.getenv("MYSQL_HOST")
    MYSQL_PORT = os.getenv("MYSQL_PORT")
    MYSQL_DATABASE = os.getenv("MYSQL_DATABASE")
    ORIGINS = [o.strip() for o in os.getenv("ORIGINS", "").split(",") if o.strip()]

settings = Settings()