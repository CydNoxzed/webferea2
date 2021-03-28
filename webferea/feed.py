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
from .helpers import handle_actions_before
from .helpers import login_required
from .helpers import format_datetime

bp = Blueprint("feed", __name__)


@bp.route('/page/<int:page>/', methods=['POST', 'GET'])
@bp.route('/', methods=['POST', 'GET'])
@handle_actions_before
@login_required
def show_feed(page=1):
    """ Show the list page for the given page number
    :param page:
    """

    # Set the page to 1 if the show_read session was changed
    # resetPage = doListActions()
    # page = 1 if resetPage else page

    node_filter = current_app.config['NODES']
    items_per_page = current_app.config['ITEMS_PER_PAGE']

    # statistics = getStatistics(node_filter)
    # get_last_sync()
    # infobar = getStatisticString( statistics )

    # pagination
    entries = db.get_items_by_node_titles(node_filter)
    p = pagination(page, items_per_page, len(entries))
    entries = items_from_pagination(entries, page, items_per_page)
    entries = decorate_entities_with_separator(entries)

    # if not entries and page != 1:
    #    abort(404)

    # save the current page in the session
    session["page"] = page

    words_per_minute = current_app.config['WORDS_PER_MINUTE']

    return render_template('feed.html', entries=entries, pagination=p, infobar={}, wpm=words_per_minute)


def items_from_pagination(items, page, items_per_page):
    """ Returns the items for the given pagination
    :param items:
    :param page:
    :param items_per_page:
    :return:
    """
    first = (page * items_per_page) - items_per_page
    last = first + items_per_page
    return items[first:last]


def pagination(page, per_page, total_count):
    """ Creates the pagination navigation for the given page information
    :param page:
    :param per_page:
    :param total_count:
    :return:
    """
    paginator = {
        "page": page,
        "has_prev": bool(page > 1),
        "has_next": bool(page < (total_count / per_page)),
        "curr_link": f"/page/{page}/",

        "prev_link": f"/page/{page - 1}/" if page > 2 else "/",
        "next_link": f"/page/{page + 1}/"
    }
    return paginator


def decorate_entities_with_separator(entries):
    """ Add an date separator entity between item entities with a different date
    :param entries:
    :return:
    """
    decorated_entries = []
    curr_date = ""

    for entry in entries:
        date = datetime.datetime.fromtimestamp(entry['date'])
        date_string = date.strftime('%Y-%m-%d')
        if (curr_date == "") or (curr_date != date_string):
            curr_date = date_string
            decorated_entries.append(get_separator(curr_date))
        decorated_entries.append(entry)
    return decorated_entries


def get_separator(text):
    """ Create a separator entity with the given text
    :param text:
    :return:
    """
    return {
        "typ": 'separator',
        "text": text
    }
