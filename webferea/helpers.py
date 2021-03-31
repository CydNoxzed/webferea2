import functools
import datetime
import os
import base64

from flask import current_app
from flask import session
from flask import url_for
from flask import redirect
from flask import request
from flask import flash
from flask import abort

from . import db


def handle_actions_before(view):
    """View decorator that redirects anonymous users to the login page."""

    @functools.wraps(view)
    def wrapped_view(**kwargs):
        kwargs = handle_actions(**kwargs)
        return view(**kwargs)

    return wrapped_view


def handle_actions(**kwargs):
    """ Perform the actions on the item view to the given item_id
    :return: kwargs
    """

    msg = ''
    action = request.form.get('action')
    item_id = request.form.get('item_id')
    if not action:
        return kwargs

    # Set the page to 1 if the show_read session was changed
    if action == "show_read" and not item_id:
        session["show_read"] = True
        msg = "Show read items"
        kwargs['page'] = 1
    if action == "hide_read" and not item_id:
        session["show_read"] = False
        msg = "Hide read items"
        kwargs['page'] = 1

    if item_id:
        if action == "read":
            ret = db.set_item_flags(item_id, action)
            msg = "Set read flag" if ret else "Cant set read flag"
        elif action == "unread":
            ret = db.set_item_flags(item_id, action)
            msg = "Unset read flag" if ret else "Cant unset read flag"
        elif action == "mark":
            ret = db.set_item_flags(item_id, action)
            msg = "Set marked flag" if ret else "Cant set marked flag"
        elif action == "unmark":
            ret = db.set_item_flags(item_id, action)
            msg = "Unset marked flag" if ret else "Cant unset marked flag"

    if msg and len(msg) > 0:
        flash(msg)

    return kwargs


def check_for_basic_auth():
    authorization = request.headers.get('Authorization')
    if authorization is None:
        abort(401, "BasicAuth Authorization required")

    authparts = authorization.split(" ")
    if len(authparts) != 2 or authparts[0].lower() != 'basic':
        abort(401, "BasicAuth Authorization required")

    client_verification = base64.b64decode(authparts[1]).decode('utf-8')
    server_verification = f"{current_app.config['USERNAME']}:{current_app.config['PASSWORD']}"
    if client_verification != server_verification:
        abort(401, "BasicAuth Authorization failed")


def login_required(view):
    """View decorator that redirects anonymous users to the login page."""

    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if not session.get('logged_in'):
            return redirect(url_for("auth.login"))

        return view(**kwargs)

    return wrapped_view


def format_datetime(timestamp) -> str:
    """ Format the given timestamp to a more readable format
    :param timestamp:
    :return:
    """
    format = '%Y-%m-%d %H:%M:%S'
    return datetime.datetime.fromtimestamp(timestamp).strftime(format)


def is_sqlite3_stream(stream) -> bool:
    """ Check if the sqlite3file is valid
    credits to: http://stackoverflow.com/questions/12932607/
    :param stream
    :return: True|False
    """
    header = stream.read(16)
    stream.seek(0)
    if header == b'SQLite format 3\000':
        return True
    return False


def set_last_sync():
    """ Sets the information of the latest database update to the flat file
    :return:
    """

    filepath = os.path.join(current_app.instance_path, 'last_updated')
    with open(filepath, "w") as text_file:
        text_file.write(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))


def get_last_sync():
    filepath = os.path.join(current_app.instance_path, 'last_updated')
    data = ''
    with open(filepath, 'r') as file:
        data = file.read().replace('\n', '')
    return data
