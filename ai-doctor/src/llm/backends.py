from typing import List, Dict

class LLMBackend:
    def chat(self, messages: List[Dict[str, str]]) -> str:
        raise NotImplementedError

    @property
    def supports_vision(self) -> bool:
        return False
