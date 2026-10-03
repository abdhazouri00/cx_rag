from fastapi import FastAPI
from routes import base,data,nlp
from helpers.config import get_settings, get_database_url
from contextlib import asynccontextmanager
from stores.llm.LLMProviderFactory import LLMProviderFactory
from stores.vectordb.VectordbProviderFactory import VectordbProviderFactory
from stores.llm.templates.template_parser import TemplateParser
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

# uv run fastapi dev main.py

@asynccontextmanager
async def lifespan(app: FastAPI):
  print("connecting to mssql")
  settings = get_settings()

  mssql_conn = get_database_url(settings)

  app.state.db_engine = create_async_engine(mssql_conn)

  app.state.db_client = sessionmaker(app.state.db_engine, expire_on_commit=False, class_=AsyncSession)

  llm_provider_factory = LLMProviderFactory(config=settings)
  vectordb_provider_factory = VectordbProviderFactory(config=settings)

  app.state.generation_client = llm_provider_factory.create(settings.GENERATION_BACKEND)
  app.state.generation_client.set_generation_model(model_id=settings.GENERATION_MODEL_ID)

  app.state.embedding_client = llm_provider_factory.create(provider=settings.EMBEDDING_BACKEND)
  app.state.embedding_client.set_embedding_model(model_id=settings.EMBEDDING_MODEL_ID, embedding_size=settings.EMBEDDING_MODEL_SIZE)

  app.state.vectordb_client = vectordb_provider_factory.create(provider=settings.VECTOR_DB_BACKEND)

  app.state.vectordb_client.connect()

  app.state.template_parser = TemplateParser(language=settings.DEFAULT_LANGUAGE, default_language=settings.DEFAULT_LANGUAGE)

  yield
  print("closing mssql connection")
  await app.state.db_engine.dispose()
  app.state.vectordb_client.disconnect()

  
app = FastAPI(lifespan=lifespan) 

app.include_router(base.base_router)
app.include_router(data.data_router)
app.include_router(nlp.nlp_router)