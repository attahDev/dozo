from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_mail import Mail
from flask_bcrypt import Bcrypt
from flask_wtf.csrf import CSRFProtect
from config import configs
import os

db      = SQLAlchemy()
migrate = Migrate()
login   = LoginManager()
mail    = Mail()
bcrypt  = Bcrypt()
csrf    = CSRFProtect()

login.login_view             = 'auth.login'
login.login_message          = 'Please sign in to continue.'
login.login_message_category = 'warning'

_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def create_app(env: str = None) -> Flask:
    env = env or os.environ.get('FLASK_ENV', 'development')
    app = Flask(
        __name__,
        template_folder=os.path.join(_root, 'templates'),
        static_folder=os.path.join(_root, 'static'),
        static_url_path='/static',         
    )
    app.config.from_object(configs[env])

    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)
    mail.init_app(app)
    bcrypt.init_app(app)
    csrf.init_app(app)

    from app.routes.auth  import auth_bp
    from app.routes.todos import todos_bp
    from app.routes.main  import main_bp
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp,  url_prefix='/auth')
    app.register_blueprint(todos_bp, url_prefix='/todos')

    @app.errorhandler(404)
    def not_found(_):    return render_template('error.html', code=404, msg='Page not found'), 404

    @app.errorhandler(500)
    def server_error(_): return render_template('error.html', code=500, msg='Internal server error'), 500

    from datetime import date
    app.jinja_env.globals['today'] = date.today

    return app