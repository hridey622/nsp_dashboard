from dotenv import load_dotenv
import os

load_dotenv()

class Config:
    DEBUG = os.getenv('DEBUG', 'False') == 'True'
    TESTING = os.getenv('TESTING', 'False') == 'True'
    DATABASE_URI = os.getenv('DATABASE_URI', 'postgresql://user:password@localhost/dbname')
    SECRET_KEY = os.getenv('SECRET_KEY', 'your_secret_key')
    JSON_SORT_KEYS = False

class DevelopmentConfig(Config):
    DEBUG = True
    DATABASE_URI = os.getenv('DEV_DATABASE_URI', 'postgresql://user:password@localhost/dev_dbname')

class TestingConfig(Config):
    TESTING = True
    DATABASE_URI = os.getenv('TEST_DATABASE_URI', 'postgresql://user:password@localhost/test_dbname')

class ProductionConfig(Config):
    DATABASE_URI = os.getenv('DATABASE_URI', 'postgresql://user:password@localhost/prod_dbname')