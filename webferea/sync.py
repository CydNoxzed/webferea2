import os
import bz2
import tempfile

from flask import Blueprint
from flask import request
from flask import current_app
from flask import send_file
from flask import abort
from flask import make_response

from .helpers import is_sqlite3_data
from .helpers import set_last_sync
from .helpers import check_for_basic_auth

bp = Blueprint("sync", __name__)

COMPRESSIONS = ["bz2"]


@bp.route('/sync/upload/<compression>', methods=['POST'])
@bp.route('/sync/upload/', methods=['POST'])
def upload(compression=None):
    # to the basic auth stuff
    check_for_basic_auth()

    if compression and compression not in COMPRESSIONS:
        abort(400, 'Unsupported compression')

    # request is authorized,
    uploaded_file = request.files.get('database')
    if uploaded_file is None:
        abort(400, 'No database delivered')

    target_path = os.path.join(current_app.instance_path, current_app.config['DATABASE'])
    fd, path = tempfile.mkstemp()
    uploaded_file.save(path)
    with open(fd, 'rb') as f:
        data = decompress(compression, f.read())
        if is_sqlite3_data(data):
            with open(target_path, 'wb') as g:
                g.write(data)
        else:
            abort(400, 'No valid database delivered')

    set_last_sync()
    return 'OK', 200


@bp.route('/sync/download/<compression>', methods=['GET'])
@bp.route('/sync/download/', methods=['GET'])
def download(compression=None):
    # to the basic auth stuff
    check_for_basic_auth()

    if compression and compression not in COMPRESSIONS:
        abort(400, 'Unsupported compression')

    # send the database
    database_path = os.path.join(current_app.instance_path, current_app.config['DATABASE'])

    with open(database_path, 'rb') as f:
        data = compress(compression, f.read())
        response = make_response(data)
        response.headers['Content-length'] = len(data)
        response.headers['Content-Encoding'] = 'application/octet-stream'
        return response


def compress(compression, data):
    if not compression:
        return data
    if compression == 'bz2':
        return bz2.compress(data, compresslevel=9)


def decompress(compression, data):
    if not compression:
        return data
    if compression == 'bz2':
        return bz2.decompress(data)


