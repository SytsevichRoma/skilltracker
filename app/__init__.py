from flask import Flask, request, session

from app.config import Config
from app.extensions import db, login_manager, migrate, babel, bcrypt


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # ---- Extensions ----
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)

    login_manager.login_view = "auth.login"

    # ✅ Flask-Babel 4 locale selector
    def get_locale():
        lang = session.get("lang")
        if lang in app.config.get("LANGUAGES", []):
            return lang

        return request.accept_languages.best_match(app.config.get("LANGUAGES", ["uk"])) or "uk"

    babel.init_app(app, locale_selector=get_locale)

    # ---- Blueprints ----
    from app.routes.main import main_bp
    from app.routes.auth import auth_bp
    from app.routes.goals import goals_bp
    from app.routes.tasks import tasks_bp
    from app.routes.calendar import calendar_bp
    from app.routes.i18n import i18n_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(goals_bp)
    app.register_blueprint(tasks_bp)
    app.register_blueprint(calendar_bp)
    app.register_blueprint(i18n_bp)

    return app
