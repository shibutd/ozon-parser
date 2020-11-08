import os
from dotenv import load_dotenv

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

dotenv_path = os.path.join(BASE_DIR, '.env.dev')
load_dotenv(dotenv_path)


class Config:
    PORT = 5000
    HOST = "127.0.0.1"
    SECRET_KEY = os.getenv('SECRET_KEY', 'hard_to_guess_string')
    SQLALCHEMY_ECHO = False
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    PAGINATION_PAGE_SIZE = 10
    PAGINATION_PAGE_ARGUMENT_NAME = 'page'


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = "postgresql://{DB_USER}:{DB_PASSWORD}@\
{DB_ADDR}/{DB_NAME}".format(
        DB_USER=os.getenv('POSTGRES_USER', "postgres"),
        DB_PASSWORD=os.getenv('POSTGRES_PASSWORD', ''),
        DB_ADDR=os.getenv('POSTGRES_ADDRESS', "127.0.0.1"),
        DB_NAME=os.getenv('POSTGRES_DB', "ozon_parser"),
    )


class TestingConfig(Config):
    TESTING = True
    PAGINATION_PAGE_SIZE = 5
    SQLALCHEMY_DATABASE_URI = "postgresql://{DB_USER}:{DB_PASSWORD}@\
{DB_ADDR}/{DB_NAME}".format(
        DB_USER=os.getenv('POSTGRES_USER', "postgres"),
        DB_PASSWORD=os.getenv('POSTGRES_PASSWORD', ''),
        DB_ADDR=os.getenv('POSTGRES_ADDRESS', "127.0.0.1"),
        DB_NAME=os.getenv('POSTGRES_DB', "ozon_parser_test"),
    )
    SERVER_NAME = 'localhost.localdomain:5000'


class ProductionConfig(Config):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = "postgresql://{DB_USER}:{DB_PASSWORD}@\
{DB_ADDR}/{DB_NAME}".format(
        DB_USER=os.getenv('POSTGRES_USER', "user_name"),
        DB_PASSWORD=os.getenv('POSTGRES_PASSWORD', ''),
        DB_ADDR=os.getenv('POSTGRES_ADDRESS', "127.0.0.1"),
        DB_NAME=os.getenv('POSTGRES_DB', "db_name"),
    )


config = {
    'dev': DevelopmentConfig,
    'test': TestingConfig,
    'prod': ProductionConfig
}
