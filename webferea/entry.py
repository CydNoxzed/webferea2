import functools
import datetime

from flask import Blueprint
from flask import flash
from flask import redirect
from flask import render_template
from flask import request
from flask import session
from flask import url_for
from flask import current_app

from . import db
from . import feed
from .helpers import handle_actions_before
from .helpers import login_required

bp = Blueprint("entry", __name__)


@bp.route('/item/<int:item_id>/', methods=['POST', 'GET'])
@handle_actions_before
@login_required
def show_item(item_id):
    """ Show the item page with the item of the given id
    :param item_id:
    :return:
    """

    entry = db.get_item_by_id(item_id)
    if len(entry) == 0:
        return redirect(url_for(feed.show_feed))

    return render_template('entry.html', entry=entry)
