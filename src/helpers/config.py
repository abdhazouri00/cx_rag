from pydantic_settings import BaseSettings,SettingsConfigDict
from sqlalchemy.engine import URL
from pathlib import Path

class Settings(BaseSettings):

  APP_NAME:str
  APP_VERSION:str
  OPENAI_API_KEY:str
  FILE_ALLOWED_TYPES:list[str]
  FILE_MAX_SIZE:int
  FILE_DEFAULT_CHUNK_SIZE:int

  MSSQL_USERNAME:str
  MSSQL_PASSWORD:str
  MSSQL_HOST:str
  MSSQL_PORT:int
  MSSQL_MAIN_DATABASE:str
  MSSQL_DRIVER:str = "ODBC Driver 18 for SQL Server"

  GENERATION_BACKEND:str
  EMBEDDING_BACKEND:str

  OPENAI_API_KEY:str = None
  OPENAI_API_URL:str = None

  OPENROUTER_API_KEY:str = ""
  OPENROUTER_API_URL:str = "https://openrouter.ai/api/v1"

  GENERATION_MODEL_ID:str = None
  EMBEDDING_MODEL_ID:str = None
  EMBEDDING_MODEL_SIZE:int = None

  INPUT_DEFAULT_MAX_CHARACTERS:int = None
  GENERATION_DEFAULT_MAX_TOKENS:int = None
  GENERATION_DEFAULT_TEMPERATURE:float = None

  VECTOR_DB_BACKEND:str
  VECTOR_DB_URL:str
  VECTOR_DB_DISTANCE_METHOD:str = None

  RAG_MIN_SCORE:float = 0.3
  CHAT_HISTORY_LIMIT:int = 5

  DEFAULT_LANGUAGE:str = "en"
  class Config:
    env_file = Path(__file__).parent.parent.parent / ".env"

def get_settings():
  return Settings()

def get_database_url(settings:Settings, database:str = None):
  return URL.create(
    "mssql+aioodbc",
    username=settings.MSSQL_USERNAME,
    password=settings.MSSQL_PASSWORD,
    host=settings.MSSQL_HOST,
    port=settings.MSSQL_PORT,
    database=database or settings.MSSQL_MAIN_DATABASE,
    query={"driver": settings.MSSQL_DRIVER, "TrustServerCertificate": "yes"},
  )
