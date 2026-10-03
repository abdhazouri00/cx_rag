from enum import Enum

class LLMEnum(Enum):
  OPENAI = "OPENAI"
  OPENROUTER = "OPENROUTER"

class OpenAIEnum(Enum):
  SYSTEM = "system"
  USER = "user"
  ASSISTANT = "assistant"

class OpenRouterEnum(Enum):
  SYSTEM = "system"
  USER = "user"
  ASSISTANT = "assistant"

class DocumentTypeEnum(Enum):
  DOCUMENT = "DOCUMENT"
  QUERY = "QUERY"
