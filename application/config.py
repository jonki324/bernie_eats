import os


class Config(object):
    DEBUG = False
    TESTING = False
    DB_USER = 'dbuser'
    DB_PASS = 'dbpass'
    DB_HOST = 'localhost'
    DB_PORT = '5432'
    DB_URI = 'postgresql+psycopg2://{}:{}@{}:{}/bernie_eats'.format(DB_USER, DB_PASS,
                                                                    DB_HOST, DB_PORT)
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.environ.get('SECRET_KEY', default=os.urandom(24))
    WTF_CSRF_SECRET_KEY = os.environ.get('WTF_CSRF_SECRET_KEY', default=os.urandom(24))


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', default=Config.DB_URI)


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = Config.DB_URI


class TestingConfig(Config):
    DEBUG = True
    TESTING = True
    WTF_CSRF_ENABLED = False
