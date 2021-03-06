import os

# uncomment the line below for postgres database url from environment variable
# postgres_local_base = os.environ['DATABASE_URL']

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'my_precious_secret_key')
    DEBUG = False
    ELASTICSEARCH_GLOSSARY = 'alegre_glossary'
    ELASTICSEARCH_URL = os.getenv('ELASTICSEARCH_URL') or 'http://elasticsearch:9200'
    ELASTICSEARCH_SIMILARITY = 'alegre_similarity'
    REDIS_HOST = os.getenv('REDIS_HOST') or 'redis'
    REDIS_PORT = os.getenv('REDIS_PORT') or 6379
    REDIS_DATABASE = os.getenv('REDIS_DATABASE') or 0
    PROVIDER_LANGID = os.getenv('PROVIDER_LANGID') or 'google'
    MS_TEXT_ANALYTICS_KEY = os.getenv('MS_TEXT_ANALYTICS_KEY')
    MS_TEXT_ANALYTICS_URL = os.getenv('MS_TEXT_ANALYTICS_URL') or 'https://westcentralus.api.cognitive.microsoft.com/text/analytics/v2.1/'


class DevelopmentConfig(Config):
    # uncomment the line below to use postgres
    # SQLALCHEMY_DATABASE_URI = postgres_local_base
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'flask_boilerplate_main.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class TestingConfig(Config):
    DEBUG = True
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, '../test/flask_boilerplate_test.db')
    PRESERVE_CONTEXT_ON_EXCEPTION = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    ELASTICSEARCH_GLOSSARY = 'alegre_glossary_test'
    ELASTICSEARCH_SIMILARITY = 'alegre_similarity_test'
    REDIS_DATABASE = 1


class ProductionConfig(Config):
    DEBUG = False
    # uncomment the line below to use postgres
    # SQLALCHEMY_DATABASE_URI = postgres_local_base


config_by_name = dict(
    dev=DevelopmentConfig,
    test=TestingConfig,
    prod=ProductionConfig
)

key = Config.SECRET_KEY
