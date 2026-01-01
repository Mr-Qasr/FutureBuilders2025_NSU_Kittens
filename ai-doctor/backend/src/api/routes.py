# backend/src/api/routes.py

from flask import Blueprint, request, jsonify
from datetime import datetime

from src.ai.diagnosis_orchestrator import DiagnosisOrchestrator
from src.core.runtime_config import runtime_config, set_model

from werkzeug.utils import secure_filename


orchestrator = DiagnosisOrchestrator()

# 1) Define the main API blueprint FIRST
api_bp = Blueprint("api", __name__, url_prefix="/api/v1")

# 2) Main API routes


@api_bp.route("/health/status", methods=["GET"])
def health_status():
    return (
        jsonify(
            {
                "status": "healthy",
                "timestamp": datetime.utcnow().isoformat(),
            }
        ),
        200,
    )


@api_bp.route("/symptom/analyze", methods=["POST"])
def analyze_symptoms():
    data = request.get_json(silent=True) or {}
    symptoms = data.get("symptoms") or []
    free_text = data.get("description")
    language = data.get("language", "en")

    context = {
        "age": data.get("age"),
        "gender": data.get("gender"),
        "known_conditions": data.get("known_conditions", []),
        "region": data.get("region"),
    }

    image_description = data.get("image_description")

    result = orchestrator.analyze(
        symptoms=symptoms,
        free_text=free_text,
        context=context,
        language=language,
        image_description=image_description,
    )

    return jsonify(result), 200


# 3) Admin blueprint for runtime model control

admin_bp = Blueprint("admin", __name__, url_prefix="/api/v1/admin")


@admin_bp.route("/models", methods=["GET"])
def get_models():
    """Return current active model names."""
    return jsonify({"status": "success", "models": runtime_config}), 200


@admin_bp.route("/models", methods=["POST"])
def update_models():
    """Update one or more model names at runtime."""
    data = request.get_json(silent=True) or {}

    changed = {}
    for key in ["REASONING_MODEL", "EXPLAIN_MODEL", "VISION_MODEL"]:
        if key in data and isinstance(data[key], str) and data[key].strip():
            set_model(key, data[key].strip())
            changed[key] = data[key].strip()

    return (
        jsonify({"status": "success", "updated": changed, "current": runtime_config}),
        200,
    )


@api_bp.route("/image/analyze", methods=["POST"])
def analyze_image():
    """Analyze a medical image (rash, wound, swelling, etc.)."""
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded (expected 'file' field)"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "Empty filename"}), 400

    try:
        image_bytes = file.read()
        if not image_bytes:
            return jsonify({"error": "Empty file"}), 400

        from src.ai.diagnosis_orchestrator import analyze_image_with_ollama

        result = analyze_image_with_ollama(image_bytes)

        return (
            jsonify(
                {
                    "status": "success",
                    "image_assessment": result,
                }
            ),
            200,
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@api_bp.route("/system/profile", methods=["GET"])
def system_profile():
    from src.system.capabilities import classify_machine, get_total_ram_gb
    from src.system.model_planner import plan_models

    tier = classify_machine()
    ram_gb = round(get_total_ram_gb(), 1)
    models = plan_models()

    return jsonify({
        "tier": tier,
        "ram_gb": ram_gb,
        "models": models,
    }), 200

