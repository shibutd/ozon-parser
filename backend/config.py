import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    PORT = 5000
    HOST = "127.0.0.1"
    SECRET_KEY = os.getenv('SECRET_KEY', 'hard_to_guess_string')
    SQLALCHEMY_ECHO = False
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    PAGINATION_PAGE_SIZE = 5
    PAGINATION_PAGE_ARGUMENT_NAME = 'page'


class DevelopmentConfig(Config):
    DEBUG = True
    # SQLALCHEMY_ECHO = True
    SQLALCHEMY_DATABASE_URI = "postgresql://{DB_USER}:{DB_PASSWORD}@\
{DB_ADDR}/{DB_NAME}".format(
        DB_USER="postgres",
        DB_PASSWORD=os.getenv('DB_PASSWORD', ''),
        DB_ADDR="127.0.0.1",
        DB_NAME="ozon_parser"
    )


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "postgresql://{DB_USER}:{DB_PASSWORD}@\
{DB_ADDR}/{DB_NAME}".format(
        DB_USER="postgres",
        DB_PASSWORD=os.getenv('DB_PASSWORD', ''),
        DB_ADDR="127.0.0.1",
        DB_NAME="ozon_parser_test"
    )
    SERVER_NAME = '127.0.0.1:5000'


class ProductionConfig(Config):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = "postgresql://{DB_USER}:{DB_PASSWORD}@\
{DB_ADDR}/{DB_NAME}".format(
        DB_USER="user_name",
        DB_PASSWORD=os.getenv('DB_PASSWORD', ''),
        DB_ADDR="127.0.0.1",
        DB_NAME="db_name"
    )


config = {
    'dev': DevelopmentConfig,
    'test': TestingConfig,
    'prod': ProductionConfig
}
