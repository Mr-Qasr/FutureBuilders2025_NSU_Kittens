from pathlib import Path
from typing import Dict

BASE_DIR = Path(__file__).resolve().parents[2]  # adjust if needed
MODELS_DIR = BASE_DIR / "models"

MODEL_FILES: Dict[str, str] = {
    "openchat:3.5-q3": "reasoning/openchat-3.5-1210.Q3_K_S.gguf",
    "gemma:2b": "reasoning/gemma-2b.gguf",
    "qwen3:8b": "reasoning/qwen3-8b.gguf",
    "qwen2.5vl:7b": "vision/qwen2.5-vl-7b.gguf",
}

def get_model_path(model_name: str) -> Path:
    rel = MODEL_FILES[model_name]
    return MODELS_DIR / rel
