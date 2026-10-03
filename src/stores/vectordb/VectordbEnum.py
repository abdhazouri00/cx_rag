from enum import Enum

class VectordbEnum(Enum):
  QDRANT = "QDRANT"

class DistanceMethodEnums(Enum):
  COSINE = "cosine"
  DOT = "dot"