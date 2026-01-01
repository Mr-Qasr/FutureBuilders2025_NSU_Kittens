from flask import Flask, app
from flask_cors import CORS

from src.core.config import config
from src.core.logger import logger
from src.api.routes import api_bp
from src.api.routes import api_bp, admin_bp


def create_app() -> Flask:
    app = Flask(__name__)
    app.config["SECRET_KEY"] = config.SECRET_KEY
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    app.register_blueprint(api_bp)
    app.register_blueprint(admin_bp)

    @app.errorhandler(500)
    def handle_500(err):
        logger.exception("Internal error: %s", err)
        return {"status": "error", "message": "Internal server error"}, 500

    return app


if __name__ == "__main__":
    app = create_app()
    logger.info("Starting offline AI server on %s:%s", config.API_HOST, config.API_PORT)
    app.run(host=config.API_HOST, port=config.API_PORT, debug=config.DEBUG)
