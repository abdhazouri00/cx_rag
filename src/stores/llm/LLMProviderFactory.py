from stores.llm.providers import OpenaiProvider
from stores.llm.providers import OpenRouterProvider
from stores.llm.LLMEnum import LLMEnum

class LLMProviderFactory:
  def __init__(self , config: dict):
    self.config = config

  def create(self,provider: str):
    if provider == LLMEnum.OPENAI.value:
      return OpenaiProvider(
        api_key=self.config.OPENAI_API_KEY,
        api_url=self.config.OPENAI_API_URL,
        default_input_max_characters = self.config.INPUT_DEFAULT_MAX_CHARACTERS,
        default_generation_max_output_tokens = self.config.GENERATION_DEFAULT_MAX_TOKENS,
        temperature=self.config.GENERATION_DEFAULT_TEMPERATURE)

    if provider == LLMEnum.OPENROUTER.value:
      return OpenRouterProvider(
        api_key=self.config.OPENROUTER_API_KEY,
        api_url=self.config.OPENROUTER_API_URL,
        default_input_max_characters = self.config.INPUT_DEFAULT_MAX_CHARACTERS,
        default_generation_max_output_tokens = self.config.GENERATION_DEFAULT_MAX_TOKENS,
        temperature=self.config.GENERATION_DEFAULT_TEMPERATURE)

    return None
