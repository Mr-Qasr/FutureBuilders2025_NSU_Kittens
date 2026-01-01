"""Core configuration for the offline AI backend."""

import os
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

load_dotenv(os.path.join(BASE_DIR, ".env"))


class Config:
    """Central config loaded from environment variables."""

    DEBUG = os.getenv("DEBUG", "True").lower() == "true"

    # Flask
    API_HOST = os.getenv("API_HOST", "0.0.0.0")
    API_PORT = int(os.getenv("API_PORT", 5000))
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")

    # Local LLM endpoints (Ollama-style)
    # Adjust if you run different ports or servers
    QWEN_REASONING_ENDPOINT = os.getenv("QWEN_REASONING_ENDPOINT", "http://localhost:11434/v1/chat/completions")
    QWEN_REASONING_MODEL = os.getenv("QWEN_REASONING_MODEL", "qwen3:8b")


    LLAMA_EXPLAIN_ENDPOINT = os.getenv("LLAMA_EXPLAIN_ENDPOINT", "http://localhost:11434/v1/chat/completions")
    LLAMA_EXPLAIN_MODEL = os.getenv("LLAMA_EXPLAIN_MODEL", "llama3:8b")

    QWEN_VL_ENDPOINT = os.getenv("QWEN_VL_ENDPOINT", "http://localhost:11434/v1/chat/completions")
    QWEN_VL_MODEL = os.getenv("QWEN_VL_MODEL", "qwen2.5-vl:7b")

    USE_LLM_REASONING = os.getenv("USE_LLM_REASONING", "True").lower() == "true"
    USE_LLM_EXPLANATION = os.getenv("USE_LLM_EXPLANATION", "True").lower() == "true"
    USE_VL_IMAGES = os.getenv("USE_VL_IMAGES", "True").lower() == "true"

    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE = os.getenv("LOG_FILE", os.path.join(BASE_DIR, "logs", "aidoctor.log"))


config = Config()
