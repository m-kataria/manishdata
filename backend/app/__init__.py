from flask import Flask, jsonify
from flask_cors import CORS

from .config import Config
from .extensions import db, login_manager


def create_app(config_class: type[Config] = Config) -> Flask:
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    login_manager.init_app(app)

    CORS(
        app,
        resources={r"/api/*": {"origins": app.config["FRONTEND_ORIGIN"]}},
        supports_credentials=True,
    )

    from .models.user import User

    @login_manager.user_loader
    def load_user(user_id: str) -> User | None:
        user = db.session.get(User, int(user_id))
        if user is None or not user.is_active:
            return None
        return user

    @login_manager.unauthorized_handler
    def unauthorized():
        return jsonify({"error": "unauthorized"}), 401

    from .routes import auth, bc, integrations, inventory, jobs, quotes, sf, users

    app.register_blueprint(auth.bp)
    app.register_blueprint(jobs.bp)
    app.register_blueprint(quotes.bp)
    app.register_blueprint(inventory.bp)
    app.register_blueprint(bc.bp)
    app.register_blueprint(sf.bp)
    app.register_blueprint(integrations.bp)
    app.register_blueprint(users.bp)

    @app.route("/api/health")
    def health():
        return jsonify({"status": "ok"})

    return app
