import functools
import datetime
import os
import base64
import re
from urllib.parse import urlsplit, urlunsplit, SplitResult
from pprint import pprint

from flask import current_app
from flask import session
from flask import url_for
from flask import redirect
from flask import request
from flask import flash
from flask import abort
import jinja2

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
        item = db.get_item_by_id(item_id)
        title = jinja2.filters.do_truncate(None, item['title'], 45, False, '...', 0)
        if action == "read":
            ret = db.set_item_flags(item_id, action)
            msg = f"Read: <em>{title}</em>" if ret else "Cant set read flag"
        elif action == "unread":
            ret = db.set_item_flags(item_id, action)

            msg = f"Unread: <em>{title}</em>" if ret else "Cant unset read flag"
        elif action == "mark":
            ret = db.set_item_flags(item_id, action)
            msg = f"Marked: <em>{title}</em>" if ret else "Cant set marked flag"
        elif action == "unmark":
            ret = db.set_item_flags(item_id, action)
            msg = f"Unmarked: <em>{title}</em>" if ret else "Cant unset marked flag"

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


def format_iframes(content) -> str:
    regex = r"(<iframe[^=>]*src=[\'\"]([^\"\'>]*)[\'\"][^>]*>)"
    matches = re.findall(regex, content, re.MULTILINE)
    for iframe, url in matches:
        replace = f'[IFRAME] <a href="{url}">{url}</a> [/IFRAME]'
        content = content.replace(iframe, replace)
    return content


def format_internal_links(content, link_prefix="/") -> str:
    regex = r"(<img[^=>]*src=[\'\"]/([^\"\'>]*)[\'\"][^>]*>)"
    matches = re.findall(regex, content, re.MULTILINE)
    for link, url in matches:
        content = content.replace(f'/{url}', f'{link_prefix}{url}')
    return content


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
    try:
        filepath = os.path.join(current_app.instance_path, 'last_updated')
        with open(filepath, "w") as text_file:
            text_file.write(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    except:
        pass


def get_last_sync():
    try:
        filepath = os.path.join(current_app.instance_path, 'last_updated')
        data = ''
        with open(filepath, 'r') as file:
            data = file.read().replace('\n', '')
        return data
    except:
        return "0000-00-00"


def get_base_url(url):
    split_url_dict = dict(urlsplit(url)._asdict())
    split_url_dict['path'] = '/'
    return urlunsplit(SplitResult(**split_url_dict))
