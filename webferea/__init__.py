import os
import json

from flask import Flask


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    default_config = {
        "SECRET_KEY": os.environ.get("SECRET_KEY", default='dev'),
        "HOST": os.environ.get("FLASK_RUN_HOST", default="0.0.0.0"),
        "PORT": os.environ.get("FLASK_RUN_PORT", default=8000),

        "DATABASE": os.environ.get("WEBFEREA_DATABASE", default='liferea.db'),
        "SHOW_READ_ENTITIES_PER_DEFAULT": os.environ.get("WEBFEREA_SHOW_READ_ENTITIES_PER_DEFAULT", default=False),
        "ITEMS_PER_PAGE": os.environ.get("WEBFEREA_ITEMS_PER_PAGE", default=10),
        "WORDS_PER_MINUTE": os.environ.get("WEBFEREA_WORDS_PER_MINUTE", default=240),

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
    from .helpers import format_datetime, format_iframes, format_internal_links

    db.init_app(app)
    app.register_blueprint(auth.bp)
    app.register_blueprint(feed.bp)
    app.register_blueprint(entry.bp)
    app.register_blueprint(sync.bp)

    app.jinja_env.filters['datetime'] = format_datetime
    app.jinja_env.filters['iframes'] = format_iframes
    app.jinja_env.filters['internal_links'] = format_internal_links

    return app
