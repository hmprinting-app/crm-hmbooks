from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from config import Config

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Silakan login terlebih dahulu.'

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    from app.routes.auth      import auth_bp
    from app.routes.dashboard import dashboard_bp
    from app.routes.leads     import leads_bp
    from app.routes.pipeline  import pipeline_bp
    from app.routes.followup  import followup_bp
    from app.routes.api       import api_bp
    from app.routes.webhooks  import webhooks_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(leads_bp)
    app.register_blueprint(pipeline_bp)
    app.register_blueprint(followup_bp)
    app.register_blueprint(api_bp)
    app.register_blueprint(webhooks_bp)

    return app
