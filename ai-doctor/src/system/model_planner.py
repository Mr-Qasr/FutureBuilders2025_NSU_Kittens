from typing import Dict
from .capabilities import classify_machine

def plan_models() -> Dict[str, str]:
    tier = classify_machine()

    cfg: Dict[str, str] = {
        "REASONING_MODEL": "gemma:2b",   # always safe
        "EXPLAIN_MODEL": "gemma:2b",
        "VISION_MODEL": "",              # off by default
    }

    if tier == "MEDIUM":
        cfg["EXPLAIN_MODEL"] = "llama3:8b"

    if tier == "HIGH":
        cfg["REASONING_MODEL"] = "qwen3:8b"
        cfg["EXPLAIN_MODEL"] = "qwen3:8b"
        cfg["VISION_MODEL"] = "qwen2.5vl:7b"

    return cfg
