from stores.vectordb.providers import qdrantdb
from .VectordbEnum import VectordbEnum

class VectordbProviderFactory:
  def __init__(self,config):
    self.config = config

  def create(self,provider: str):
    if provider == VectordbEnum.QDRANT.value:
      return qdrantdb(db_url=self.config.VECTOR_DB_URL, distance_method=self.config.VECTOR_DB_DISTANCE_METHOD)

    return None
