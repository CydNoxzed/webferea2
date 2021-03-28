import sqlite3
import os

import click
from flask import current_app, g
from flask.cli import with_appcontext
from flask import session


def init_db():
    db = get_db()

    # Add the column 'webferea' to the table items
    query = """PRAGMA table_info(items)"""
    cur = db.execute(query)
    entries = cur.fetchall()
    has_field = False
    for i in entries:
        if i["name"] == "webferea":
            has_field = True

    if not has_field:
        query = '''ALTER TABLE items ADD COLUMN webferea DATETIME;'''
        db.execute(query)
        db.commit()


@click.command('init-db')
@with_appcontext
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')


def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)


def get_db():
    if 'db' not in g:
        db_file = os.path.join(current_app.instance_path, current_app.config['DATABASE'])
        g.db = sqlite3.connect(
            db_file,
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row

    return g.db


def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()


def get_items_by_node_titles(node_titles):
    """ Returns all items which are linked to the given node_title

    :param node_titles:
    :return:
    """

    db = get_db()

    hide_read_snipplet = "OR (webferea <> '')" if session["show_read"] else ""

    query = """
        SELECT 
            items.*, 
            node.title AS node_title 
        FROM items 
        JOIN node 
            ON node.node_id = items.node_id
        WHERE 
            node.title IN ('%s')
            AND items.comment = 0 
            AND (( 
                    items.read = 0 
                    AND items.marked = 0 
                ) %s )
            ORDER BY items.date DESC
        """ % ("', '".join(node_titles), hide_read_snipplet)

    cur = db.execute(query)
    entries = cur.fetchall()
    return entries


def get_item_by_id(id):
    """ Get the single item from the database with the given id.
    :param id:
    :return:
    """
    db = get_db()
    params = {
        "id": id,
    }
    cur = db.execute('''
        SELECT 
            items.*, 
            node.title AS node_title
        FROM items 
        JOIN node
            ON items.node_id = node.node_id
        WHERE item_id = :id
        ''', params)
    entries = cur.fetchall()
    return entries[0]


def set_item_flags(item_id, action):
    """ Sets the flag of the given item_id by the action
    :param item_id:
    :param action:
    :return:
    """

    db = get_db()
    update = ""

    if action == "read":
        update = "read = 1"

    elif action == "unread":
        update = "read = 0"

    elif action == "mark":
        update = "marked = 1"

    elif action == "unmark":
        update = "marked = 0"

    # Return false if the action was invalid
    if update == "":
        return False

    query = '''
        UPDATE items 
        SET {},
        webferea = DATETIME('now')
        WHERE item_id = "{}"
        '''.format(update, item_id)
    db.execute(query)
    db.commit()
    return True
