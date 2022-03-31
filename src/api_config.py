class Config(object):
    DEBUG = False
    TESTING = False

class ProductionConfig(Config):
    SERVER_NAME="localhost:3000"
    COUCHDB_SERVER="http://admin:student@localhost:5984/"
    pass

class DevelopmentConfig(Config):
    DEBUG = True
    SERVER_NAME="localhost:8080"
    COUCHDB_SERVER="http://admin:student@localhost:5984/"


class TestingConfig(Config):
    TESTING = True
    SERVER_NAME="localhost:5000"
    COUCHDB_SERVER="http://admin:student@localhost:5984/"
