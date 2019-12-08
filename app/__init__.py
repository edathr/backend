from flask import Flask
from flask_restplus import Api, reqparse
from flask_pymongo import PyMongo
from .serialization_helper import JSONEncoder
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
import copy
from flask_cors import CORS
import logging
from .logging_db import LogMongoHandler
from flask import request

# local imports
from config import app_config

# db driver variable initialization
mongo = PyMongo()

from .models import User, RevokedTokenModel, OldReview, LiveReview

# from app import models
jwt = JWTManager()

def create_app(config_name):
    print("Config name")
    print(config_name)

    app = Flask(__name__)
    if not config_name:
        config_name = "development"
    app.config.from_object(app_config[config_name])

    from .models import db
    db.init_app(app)

    print(app.config["JWT_ACCESS_TOKEN_EXPIRES"])
    migrate = Migrate(app, db)

    jwt.init_app(app)

    logging.basicConfig(filename='demo.log', level=logging.DEBUG)
    # DATABASE CONFIG
    print(app.config["MONGO_URI"])
    print(app.config["SQLALCHEMY_DATABASE_URI"])
    mongo.init_app(app)
    app.json_encoder = JSONEncoder
    books = mongo.db.kindle_metadata2
    logs = mongo.db.endpoint_logs

    try:
        print("Creating index")
        books.ensure_index([("title", "text")])
        books.ensure_index(("title"))
        books.ensure_index(("asin"))
        books.ensure_index(("genres"))
        books.ensure_index(("newly_added"))

    except Exception as e:
        print("Index already exists")

    # Allow CORS
    CORS(app, support_credentials=True)

    # app.register_blueprint(books_blueprint, url_prefix='/api/books')
    # REQUEST PARSER
    register_credentials = reqparse.RequestParser()
    register_credentials.add_argument('username', default="tester", help='Username field cannot be blank',
                                      required=True)

    register_credentials.add_argument('password', default="pleasedDoNotHack", help='Password field cannot be blank',
                                      required=True)
    login_credentials = copy.deepcopy(register_credentials)
    register_credentials.add_argument('email', default="test@example.com", help='Email field cannot be blank',
                                      required=True)


    @app.before_request
    def log_request_info():
        if len(logging.getLogger('').handlers) > 1:
            logging.getLogger('').handlers.pop()
        logdb = LogMongoHandler(logs, request)
        logging.getLogger('').addHandler(logdb)
        log = logging.getLogger('MY_LOGGER')
        log.setLevel('DEBUG')

    @app.route('/')
    def hello_world():
        """HealthCheck"""
        return "Hello World, Server is alive and well!"

    # DOCS CONFIG
    api = Api(app=app, title="FaveBook API Documentation", version="v3.2 (3 Dec)", doc="/docs/")
    from .namespaces.book import api as books_api
    from .namespaces.book_search import api as book_search_api
    from .namespaces.auth import api as auth_api
    from .namespaces.book_review import api as book_review_api
    from .namespaces.book_genre import api as book_genre_api
    from .namespaces.book_add import api as book_add_api
    from .namespaces.log_retrievals import api as log_retrieval_api

    api.add_namespace(books_api)
    api.add_namespace(auth_api)
    api.add_namespace(book_search_api)
    api.add_namespace(book_review_api)
    api.add_namespace(book_genre_api)
    api.add_namespace(book_add_api)
    api.add_namespace(log_retrieval_api)

    return app

