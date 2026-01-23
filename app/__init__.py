from flask import Flask
from .config import Config
from .extensions import db, migrate, login_manager, bcrypt
from .routes.main import main_bp
from .routes.auth import auth_bp
from .routes.goals import goals_bp
from .routes.tasks import tasks_bp
from app.routes.calendar import calendar_bp  




def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)

    login_manager.init_app(app)
    bcrypt.init_app(app)
    login_manager.login_view = "auth.login"

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(goals_bp)
    app.register_blueprint(tasks_bp)
    app.register_blueprint(calendar_bp)



    return app
