import functools
import base64
import datetime
import os
from flask import Flask, flash, request, redirect, url_for
from werkzeug.utils import secure_filename
from flask import Blueprint
from flask import request
from flask import current_app
from flask import send_file
from flask import abort

from .helpers import is_sqlite3_stream
from .helpers import set_last_sync
from .helpers import check_for_basic_auth

bp = Blueprint("sync", __name__)


# @login_required
@bp.route('/sync/test/', methods=['POST'])
def test():
    # to the basic auth stuff
    check_for_basic_auth()

    # request is authorized,
    uploaded_file = request.files.get('database')
    if uploaded_file is None:
        abort(400, 'No database delivered')

    # check if the file is a sqlite db
    if not is_sqlite3_stream(uploaded_file.stream):
        abort(400, 'No valid database delivered')

    uploaded_file.save(os.path.join(current_app.instance_path, current_app.config['DATABASE']))
    set_last_sync()
    return 'OK', 200


@bp.route('/sync/download/', methods=['POST'])
def download():
    # to the basic auth stuff
    check_for_basic_auth()

    # send the database
    database_path = os.path.join(current_app.instance_path, current_app.config['DATABASE'])
    return send_file(database_path, 'application/x-sqlite')
