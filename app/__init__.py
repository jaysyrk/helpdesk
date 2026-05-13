from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail
from flask_wtf.csrf import CSRFProtect
from config import Config

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message_category = 'info'
mail = Mail()
csrf = CSRFProtect()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    csrf.init_app(app)

    from app.routes.auth import auth_bp
    from app.routes.tickets import tickets_bp
    from app.routes.assets import assets_bp
    from app.routes.dashboard import dashboard_bp
    from app.routes.admin import admin_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(tickets_bp)
    app.register_blueprint(assets_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(admin_bp)

    with app.app_context():
        db.create_all()
        _run_migrations()
        _seed_admin()

    return app


def _run_migrations():
    """Apply lightweight schema migrations for SQLite compatibility."""
    from sqlalchemy import text
    migrations = [
        'ALTER TABLE users ADD COLUMN is_active BOOLEAN NOT NULL DEFAULT 1',
    ]
    for stmt in migrations:
        try:
            db.session.execute(text(stmt))
            db.session.commit()
        except Exception:
            db.session.rollback()  # Column already exists — safe to ignore


def _seed_admin():
    from app.models import User
    from werkzeug.security import generate_password_hash
    if not User.query.filter_by(username='admin').first():
        admin = User(
            username='admin',
            email='admin@helpdesk.local',
            password_hash=generate_password_hash('admin123'),
            role='admin',
            department='IT'
        )
        db.session.add(admin)
        db.session.commit()
