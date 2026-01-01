# backend/src/core/runtime_config.py
from typing import Dict
from src.core.config import config
from src.system.model_planner import plan_models

runtime_config = plan_models()

def get_model(name: str) -> str:
    return runtime_config.get(name, "")

def set_model(name: str, value: str) -> None:
    runtime_config[name] = value
