"""Diagnosis orchestrator using local LLMs only."""

from src.core.config import config
from src.core.logger import logger
from src.core.runtime_config import get_model
from .llm_client import LLMClient
import json
from typing import Any, Dict, List, Optional
import base64
import ollama
import requests
import json


class DiagnosisOrchestrator:
    def __init__(self) -> None:
        self.reasoner = LLMClient(
            endpoint=config.QWEN_REASONING_ENDPOINT,
            model=get_model("REASONING_MODEL"),
        )

        self.explainer = LLMClient(
            endpoint=config.LLAMA_EXPLAIN_ENDPOINT,
            model=get_model("EXPLAIN_MODEL"),
        )

        self.vision = LLMClient(
            endpoint=config.QWEN_VL_ENDPOINT,
            model=get_model("VISION_MODEL"),
        )

    def analyze_image_with_ollama(image_bytes: bytes) -> dict:
        """Use a vision model via Ollama's OpenAI-compatible HTTP API to analyze a medical image."""
        # Adjust model name to a real vision model you have, e.g. "qwen3-vl"
        model_name = "qwen3-vl"

        system_prompt = (
            "You are a medical image specialist. The image may show rashes, wounds, swelling, or other skin findings.\n"
            "Describe only what you see on the body (location, color, rash type, swelling, obvious infection signs).\n"
            "Then summarize your assessment as STRICT JSON with keys:\n"
            "  rash_type (string),\n"
            "  location (string),\n"
            '  severity ("mild"|"moderate"|"severe"),\n'
            '  infection_risk ("low"|"medium"|"high"),\n'
            "  doctor_note (string).\n"
            "Return ONLY the JSON object, nothing else."
        )

        # This assumes Ollama exposes an OpenAI-compatible /v1/chat/completions endpoint with image support
        url = "http://localhost:11434/v1/chat/completions"

        files = {
            # many implementations expect image as a separate file; adjust key name if needed
            "file": ("image.png", image_bytes, "image/png"),
        }

        data = {
            "model": model_name,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": "Analyze this medical image."},
            ],
        }

        try:
            resp = requests.post(url, json=data, timeout=60)
            resp.raise_for_status()
            result = resp.json()
            text = result["choices"][0]["message"]["content"].strip()
        except Exception as e:
            return {
                "rash_type": "unknown",
                "location": "unknown",
                "severity": "unknown",
                "infection_risk": "unknown",
                "doctor_note": f"Vision model error: {e}",
            }

        # Extract JSON object from the text
        first = text.find("{")
        last = text.rfind("}")
        if first == -1 or last == -1 or last <= first:
            return {
                "rash_type": "unknown",
                "location": "unknown",
                "severity": "unknown",
                "infection_risk": "unknown",
                "doctor_note": text,
            }

        json_str = text[first : last + 1]
        try:
            parsed = json.loads(json_str)
            return {
                "rash_type": parsed.get("rash_type", "unknown"),
                "location": parsed.get("location", "unknown"),
                "severity": parsed.get("severity", "unknown"),
                "infection_risk": parsed.get("infection_risk", "unknown"),
                "doctor_note": parsed.get("doctor_note", text),
            }
        except Exception:
            return {
                "rash_type": "unknown",
                "location": "unknown",
                "severity": "unknown",
                "infection_risk": "unknown",
                "doctor_note": text,
            }

    def _analyze_image(self, image_description: str | None) -> Optional[Dict[str, Any]]:
        """Use Qwen2.5-VL (or similar) to analyze skin/wound images.

        In practice you will probably send base64 or a URL + text.
        Here we assume you already converted the image to a short description or URL.
        """
        if not config.USE_VL_IMAGES or not image_description:
            return None

        system_prompt = (
            "You are a medical vision assistant. "
            "Given a description or reference to a skin or wound image plus some text, "
            "you return a small JSON object describing rash_type, severity, infection_risk. "
            "Use keys: rash_type, severity, infection_risk, and keep values short."
        )

        messages = [
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": f"Image info: {image_description}",
            },
        ]

        text = self.vision.chat(messages)
        if not text:
            return None

        try:
            cleaned = text.strip().strip("`")
            if cleaned.lower().startswith("json"):
                cleaned = cleaned[4:].strip()
            return json.loads(cleaned)
        except Exception:
            logger.warning("Failed to parse vision JSON: %s", text[:200])
            return None

    def _reason_with_llm(
        self,
        symptoms: List[str],
        free_text: str | None,
        context: Dict[str, Any],
        image_info: Optional[Dict[str, Any]],
    ) -> Optional[Dict[str, Any]]:
        """Use reasoning LLM to derive diagnosis, parsing JSON if present."""
        if not config.USE_LLM_REASONING:
            return None

        payload = {
            "symptoms": symptoms,
            "free_text": free_text or "",
            "patient_context": context,
            "image_analysis": image_info,  # may be None
        }

        system_prompt = (
            "You are a cautious medical doctor, not a chatbot. "
            "You receive structured data (JSON) with symptoms, brief history, and optional image findings. "
            "Your job is to think like a real clinician and produce a compact, structured assessment.\n\n"
            "You MUST return your medical reasoning inside a single ```json code block. "
            "The JSON object MUST have exactly these keys:\n"
            "  diagnoses: [ { name: string, probability: number (0-1), reasons: string } ],\n"
            "  severity: 'low' | 'medium' | 'high' | 'emergency',\n"
            "  care_level: 'self-care' | 'doctor-within-24h' | 'emergency-now',\n"
            "  medications: [ string ] (simple over-the-counter or common classes ONLY, no dosages),\n"
            "  red_flags: [ string ],\n"
            "  doctor_note: string,\n"
            "  disclaimer: string.\n\n"
            "Rules:\n"
            "- Return at most 3 diagnoses.\n"
            "- Probabilities MUST be between 0 and 1, roughly summing to 1.\n"
            "- Use short, clinical reasons (1–2 sentences max).\n"
            "- If the case is clearly mild, suggest self-care and simple meds.\n"
            "- If there is any risk of serious disease, set severity to 'high' or 'emergency' and care_level accordingly.\n"
            "- DO NOT list exact dosages, ONLY medication names or classes.\n"
            "- If image_analysis is present, factor it into your diagnoses and severity.\n"
            "- You are allowed to sound like a real doctor, but you MUST include a disclaimer."
        )

        messages = [
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": f"INPUT_JSON:\n{json.dumps(payload, ensure_ascii=False)}",
            },
        ]

        text = self.reasoner.chat(messages)
        if not text:
            return None

        text = text.strip()

        # 1) Try to extract a ```json block if present
        json_block = None
        if "```json" in text:
            try:
                start = text.index("```json") + len("```json")
                end = text.index("```", start)
                json_block = text[start:end].strip()
            except ValueError:
                json_block = None

        # 2) If we found a JSON block and can parse it, RETURN IT and do NOT fall back
        if json_block:
            try:
                parsed = json.loads(json_block)
                return parsed
            except Exception:
                logger.warning(
                    "Failed to parse JSON block from LLM: %s", json_block[:300]
                )

        # 3) If whole text looks like JSON, try that
        if text.startswith("{") and text.endswith("}"):
            try:
                return json.loads(text)
            except Exception:
                logger.warning("Failed to parse full-text JSON from LLM")

        # 4) Fallback: wrap raw text
        return {
            "diagnoses": [],
            "severity": "unknown",
            "care_level": "doctor-within-24h",
            "medications": [],
            "red_flags": [],
            "doctor_note": "Model did not return structured JSON.",
            "disclaimer": "This explanation was generated by an AI model and may not be accurate. Always consult a qualified doctor.",
            "raw_text": text,
        }

    def _explain_with_llm(
        self, structured: Dict[str, Any], language: str = "en"
    ) -> Optional[str]:
        """Use Llama 3.1 to generate user-friendly explanation."""
        if not config.USE_LLM_EXPLANATION:
            return None

        system_prompt = (
            "You are a friendly medical assistant. "
            "Given structured JSON about likely diagnoses, severity, and care_level, "
            "explain in simple language suitable for a non-expert. "
            "Keep it short (3-6 sentences), mention uncertainty, and ALWAYS tell them to see a real doctor. "
            "Do NOT list drugs or dosages. If language != 'en', translate the explanation."
        )

        messages = [
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": f"language={language}\nSTRUCTURED_JSON:\n{json.dumps(structured, ensure_ascii=False)}",
            },
        ]

        return self.explainer.chat(messages)

    def analyze(
        self,
        symptoms: List[str],
        free_text: str | None,
        context: Dict[str, Any],
        language: str = "en",
        image_description: str | None = None,
    ) -> Dict[str, Any]:
        symptoms = [s.strip().lower() for s in symptoms if s and isinstance(s, str)]

        image_info = None
        if image_description:
            image_info = {
                "description": image_description,
            }

        # later when calling LLM reasoning:
        reasoning = self._reason_with_llm(
            symptoms=symptoms,
            free_text=free_text,
            context=context,
            image_info=image_info,
        )
        structured = self._reason_with_llm(symptoms, free_text, context, image_info)

        if not structured:
            structured = {
                "diagnoses": [],
                "severity": "unknown",
                "care_level": "doctor-within-24h",
                "red_flags": [],
                "disclaimers": [
                    "This system could not confidently analyze your symptoms.",
                    "Please consult a qualified doctor for proper diagnosis.",
                ],
            }

        explanation = self._explain_with_llm(structured, language)
        result: Dict[str, Any] = {
            "status": "success",
            "structured": structured,
            "language": language,
        }

        if image_info:
            result["image_analysis"] = image_info

        if explanation:
            result["explanation"] = explanation

        return result
