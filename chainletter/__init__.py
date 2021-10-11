import os

from flask import Flask
from jinja2 import StrictUndefined


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)

    # see https://stackoverflow.com/a/33790196/512652
    database = os.path.join(app.instance_path, 'chainletter.sqlite')
    app.config.from_mapping(
        SECRET_KEY='dev',
        # DATABASE=database,
        SQLALCHEMY_DATABASE_URI=f"sqlite:///{database}",
        SQLALCHEMY_TRACK_MODIFICATIONS = False,
    )
    app.jinja_env.undefined = StrictUndefined

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # setup sqlalchemy/db
    from .models import db, cli
    db.init_app(app)
    cli.init_app(app)

    from . import auth
    app.register_blueprint(auth.bp)

    from . import chainlink
    app.register_blueprint(chainlink.bp)
    app.add_url_rule('/', endpoint='index')

    # a simple page that says hello
    @app.route('/hello')
    def hello():
        return 'Hello, World!'

    return app
