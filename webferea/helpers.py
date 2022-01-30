import functools
import datetime
import os
import base64
import re
import pathlib
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

    msgs = []
    action = request.form.get('action')
    if not action:
        return kwargs

    if action == "settings":
        # Set the page to 1 if the show_read session was changed
        show_read = request.form.get('show_read')
        if show_read == '1':
            session["show_read"] = True
            msgs.append("Show read items")
            kwargs['page'] = 1

        hide_read = request.form.get('hide_read')
        if hide_read == '1':
            session["show_read"] = False
            msgs.append("Hide read items")
            kwargs['page'] = 1

    if action == 'entry':
        item_ids = request.form.get('ids').split(",")
        for item_id in item_ids:
            item = db.get_item_by_id(item_id)
            if item:
                flags = []
                read = request.form.get('read')
                if read == '1':  # read
                    if db.set_item_flags(item_id, 'read'):
                        flags.append('Read')
                elif read == '0':  # unread
                    if db.set_item_flags(item_id, 'unread'):
                        flags.append('Unread')

                mark = request.form.get('mark')
                if mark == '1':  # mark
                    if db.set_item_flags(item_id, 'mark'):
                        flags.append('Mark')
                elif mark == '0':  # unmark
                    if db.set_item_flags(item_id, 'unmark'):
                        flags.append('Unmark')

                if len(flags) > 0:
                    title = jinja2.filters.do_truncate(None, item['title'], 45, False, '...', 0)
                    msgs.append(f"{','.join(flags)}: <em>{title}</em>")

    for msg in msgs:
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
            return redirect(url_for("auth.login", next=request.path))

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
    if content is None:
        return content
    regex = r"(<iframe[^>]*src=[\'\"]([^\"\'>]*)[\'\"][^>]*>)"
    matches = re.findall(regex, content, re.MULTILINE)
    for iframe, url in matches:
        replace = f'[IFRAME] <a href="{url}">{url}</a> [/IFRAME]'
        content = content.replace(iframe, replace)
    return content


def format_internal_links(content, link_prefix="/") -> str:
    if content is None:
        return content
    regex = [
        r"(<img[^=>]*src=[\'\"]/([^\"\'>]*)[\'\"][^>]*>)",
        r"(<a[^=>]*href=[\'\"]/([^\"\'>]*)[\'\"][^>]*>)"
    ]
    for reg in regex:
        matches = re.findall(reg, content, re.MULTILINE)
        for link, url in matches:
            if url.startswith('/'):  # ignore urls that starts with "//", cause they are protocol independent
                continue

            # convert lazy loading data-src attribute to src
            if "img" in link and " src=" not in link:
                content = content.replace(link, link.replace('-src=', ' src='))

            # replace links
            content = content.replace(f'/{url}', f'{link_prefix}{url}')


    return content


def filter_external_scripts(content, link_prefix="/") -> str:
    if content is None:
        return content
    regex = r"(<script[^=>]*src=[\'\"]([^\"\'>]*)[\'\"][^>]*>)"
    matches = re.findall(regex, content, re.MULTILINE)
    for tag, url in matches:
        if not url.startswith("/") or link_prefix not in url:
            content = content.replace(tag, '')
    return content


def is_sqlite3_data(data) -> bool:
    return data.startswith(b'SQLite format 3\000')


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
    split_url_dict['query'] = ''
    split_url_dict['fragment'] = ''
    return urlunsplit(SplitResult(**split_url_dict))


def get_valid_theme_path(app):

    custom_themes_dir = app.config['THEMES_DIR']
    theme_name = app.config['THEME']
    theme_dir = ""

    default_themes_dir = pathlib.Path(__file__).resolve().parents[1] / 'themes' / theme_name
    instance_themes_dir = pathlib.Path(app.instance_path) / theme_name

    possible_themes_dirs = [
        # theme inside instance directory
        instance_themes_dir,
        # library default directory
        default_themes_dir,
    ]

    if custom_themes_dir.strip() != "":
        # theme dir from the environment
        possible_themes_dirs.insert(0, pathlib.Path(custom_themes_dir))

    expected_paths = ["templates", "static"]
    expected_templates = ["login.html", "feed.html", "entry.html"]

    for possible_dir in possible_themes_dirs:
        try:
            if not possible_dir.exists():
                continue
            if not subdirectories_exists(possible_dir, expected_paths):
                continue
            if not files_exists(possible_dir / 'templates', expected_templates):
                continue
            theme_dir = possible_dir
            break

        except FileNotFoundError as e:
            pass
    return theme_dir


def subdirectories_exists(path: pathlib.Path, subdirectories: list):
    for sub in subdirectories:
        p = path / sub
        if not p.exists() and not p.is_dir():
            return False
    return True


def files_exists(path: pathlib.Path, files: list):
    for file in files:
        p = path / file
        if not p.exists() and not p.is_file():
            return False
    return True




