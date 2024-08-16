#config.py

from typing import Dict, Optional, Union
from pydantic import BaseModel, Field

class ModelConfig(BaseModel):
    name: str
    provider: str
    api_base: Optional[str] = None
    max_tokens: int
    temperature: float = Field(0.7, ge=0.0, le=1.0)

class Config(BaseModel):
    default_model: str
    models: Dict[str, ModelConfig]
    rate_limit: Dict[str, Union[int, float]]
