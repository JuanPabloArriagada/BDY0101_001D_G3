from pydantic_settings import BaseSettings, SettingsConfigDict
from pymongo import MongoClient
from pymongo.errors import PyMongoError


class MongoSettings(BaseSettings):
    mongo_uri: str
    mongo_db_name: str = "eventify_db"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


try:
    settings = MongoSettings()
    client = MongoClient(settings.mongo_uri)
    db = client[settings.mongo_db_name]
except (ValueError, OSError, PyMongoError):
    raise RuntimeError("Revisa MONGO_URI y MONGO_DB_NAME en el archivo .env.") from None


def get_database():
    return db


def ping_database():
    try:
        db.command("ping")
    except PyMongoError:
        raise RuntimeError("No se pudo conectar a MongoDB. Revisa las credenciales y la red.") from None
    return True


def close_connection():
    client.close()
