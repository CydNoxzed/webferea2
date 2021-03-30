import os
import json

from flask import Flask


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    default_config = {
        "SECRET_KEY": 'dev',
        "DATABASE": 'liferea.db',
        "SHOW_READ_ENTITIES_PER_DEFAULT": False,
        "ITEMS_PER_PAGE": 10,
        "HOST": "0.0.0.0",
        "PORT": 5000,
        "WORDS_PER_MINUTE": 240,
        "NODES": ()
    }

    config_json = {}
    with open(os.path.join(app.instance_path, 'config.json')) as json_file:
        config_json = json.load(json_file)
    merged_config = {**default_config, **config_json}

    # set setting to app
    app.config.update(**merged_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # initialize the modules
    from . import db
    from . import auth
    from . import feed
    from . import entry
    from . import sync
    from .helpers import format_datetime

    db.init_app(app)
    app.register_blueprint(auth.bp)
    app.register_blueprint(feed.bp)
    app.register_blueprint(entry.bp)
    app.register_blueprint(sync.bp)

    app.jinja_env.filters['datetime'] = format_datetime

    return app
