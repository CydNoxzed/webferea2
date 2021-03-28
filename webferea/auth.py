import functools

from flask import Blueprint
from flask import flash
from flask import redirect
from flask import render_template
from flask import request
from flask import session
from flask import url_for
from flask import current_app

bp = Blueprint("auth", __name__)


@bp.route('/login/', methods=['GET', 'POST'])
def login():
    """ Handles the login page
    :return:
    """
    error = None
    if request.method == 'POST':
        if request.form.get('username') != current_app.config['USERNAME']:
            error = 'Invalid username'
        elif request.form.get('password') != current_app.config['PASSWORD']:
            error = 'Invalid password'
        else:
            session['logged_in'] = True

            # create default session keys
            if "show_read" not in session:
                session["show_read"] = current_app.config['SHOW_READ_ENTITIES_PER_DEFAULT']
            if "page" not in session:
                session["page"] = 1

            flash('You were logged in')
            return redirect(url_for('feed.show_feed'))

    # return "login.html"
    return render_template('login.html', error=error)


@bp.route("/logout/", methods=['GET', 'POST'])
def logout():
    """Clear the current session, including the stored user id."""
    session.clear()
    flash('You were logged out')
    return redirect(url_for("auth.login"))
