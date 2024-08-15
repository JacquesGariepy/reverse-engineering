import os
from .config import Config
from aider import models, coders, io
from typing import Optional

class LLMManager:
    def __init__(self, config: Config):
        self.config = config
        self.io = io.InputOutput()
        self.llms = self._initialize_llms()
        self.coders = self._initialize_coders()

    def _initialize_llms(self):
        """Initialize LLMs based on the configuration."""
        llms = {}
        for model_name, model_config in self.config.models.items():
            llm_class = getattr(models, f"{model_config.provider.capitalize()}Model")
            llms[model_name] = llm_class(
                model_name=model_name,
                api_key=os.getenv(f"{model_config.provider.upper()}_API_KEY"),
                api_base=model_config.api_base,
                temperature=model_config.temperature,
                max_tokens=model_config.max_tokens
            )
        return llms

    def _initialize_coders(self):
        """Initialize coders for each LLM."""
        return {model_name: coders.Coder(llm, self.io) for model_name, llm in self.llms.items()}
