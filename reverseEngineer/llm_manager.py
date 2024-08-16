import os
from config import Config
from aider import models, coders, io
from aider.models import Model
class LLMManager:
    def __init__(self, config: Config):
        self.config = config
        self.io = io.InputOutput()
        self.models = self._initialize_models()
        self.coders = self._initialize_coders()

    def _initialize_models(self):
        """Initialize models based on the configuration."""
        models_dict = {}
        model = Model("gpt-4-turbo")
        for model_name, model_config in self.config.models.items():
            model = models.Model(model_name)
            models_dict[model_name] = model
        return models_dict

    def _initialize_coders(self):
        """Initialize coders for each model."""
        coders_dict = {}
        for model_name, model in self.models.items():
            coder = coders.Coder.create(main_model=model, io=self.io)
            coders_dict[model_name] = coder
        return coders_dict

    def get_model(self, model_name: str):
        """Retrieve a specific model by name."""
        return self.models.get(model_name)

    def get_coder(self, model_name: str):
        """Retrieve a specific coder by model name."""
        return self.coders.get(model_name)
