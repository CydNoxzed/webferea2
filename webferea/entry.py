import functools
import datetime
from pprint import pprint

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
from . import helpers

bp = Blueprint("entry", __name__)


@bp.route('/item/<int:item_id>/', methods=['POST', 'GET'])
@helpers.handle_actions_before
@helpers.login_required
def show_item(item_id):
    """ Show the item page with the item of the given id
    :param item_id:
    :return:
    """

    entry = db.get_item_by_id(item_id)
    if len(entry) == 0:
        flash("No Item found")
        return redirect(url_for("feed.show_feed"))

    # change/filter the output of the entry
    link_prefix = helpers.get_base_url(entry["source"])
    entry['description'] = helpers.format_iframes(entry['description'])
    entry['description'] = helpers.format_internal_links(entry['description'], link_prefix)
    entry['description'] = helpers.filter_external_scripts(entry['description'], link_prefix)

    return render_template('entry.html', entry=entry)
