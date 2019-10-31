import os
from application.models import init_db
from application.views import view
from application.const import Const
from flask import Flask


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

    app.register_blueprint(view)

    app.jinja_env.globals.update(Const.__dict__)

    return app
