import os
from dotenv import load_dotenv

load_dotenv()

_root = os.path.dirname(os.path.abspath(__file__))


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'postgresql://localhost/dozo_db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {'pool_pre_ping': True, 'pool_recycle': 300}

    MAIL_SERVER         = os.environ.get('MAIL_SERVER')
    MAIL_PORT           = int(os.environ.get('MAIL_PORT'))
    MAIL_USE_TLS        = True
    MAIL_USERNAME       = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD       = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_USERNAME')

    APP_URL                 = os.environ.get('APP_URL', 'http://localhost:5000')
    REMINDER_MINUTES_BEFORE = int(os.environ.get('REMINDER_MINUTES_BEFORE'))
    SCHEDULER_INTERVAL_MINS = 15


class DevConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL',
        f'sqlite:///{os.path.join(_root, "dozo_dev.db")}'
    )
    SQLALCHEMY_ENGINE_OPTIONS = {}


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False
    SECRET_KEY = 'test-secret'
    SQLALCHEMY_ENGINE_OPTIONS = {}


configs = {'production': Config, 'development': DevConfig, 'testing': TestConfig}