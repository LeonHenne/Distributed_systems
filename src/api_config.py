class Config(object):
    DEBUG = False
    TESTING = False

class ProductionConfig(Config):
    SERVER_NAME="0.0.0.0:8080"
    COUCHDB_SERVER="http://admin:student@couchdb:5984/"
    pass

class DevelopmentConfig(Config):
    DEBUG = True
    SERVER_NAME="0.0.0.0:8080"
    COUCHDB_SERVER="http://admin:student@localhost:5984/"

class TestingConfig(Config):
    TESTING = True
    SERVER_NAME="0.0.0.0:5000"
    COUCHDB_SERVER="http://admin:student@couchdb:5984/"
