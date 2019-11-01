import os
from application.models import init_db, User
from application.views import view
from application.const import Const
from flask import Flask
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect


def create_app():
    app = Flask(__name__)

    configs = {
        'production': 'ProductionConfig',
        'development': 'DevelopmentConfig',
        'testing': 'TestingConfig'
    }
    flask_env = os.environ.get('FLASK_ENV', default='production')
    app.config.from_object('application.config.{}'.format(configs[flask_env]))

    init_db(app)

    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'view.login'
    login_manager.login_message = 'ログインしてください'
    login_manager.login_message_category = 'danger'

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.filter(User.id == user_id).first()

    csrf = CSRFProtect()
    csrf.init_app(app)

    app.register_blueprint(view)

    app.jinja_env.globals.update(Const.__dict__)

    return app
