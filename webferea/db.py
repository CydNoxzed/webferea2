import sqlite3
import os

import click
from flask import current_app, g
from flask.cli import with_appcontext
from flask import session
from flask import abort


def init_app(app):
    app.teardown_appcontext(close_db)


def init_db(db):
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


def get_db():
    if 'db' not in g:
        try:
            db_file = os.path.join(current_app.instance_path, current_app.config['DATABASE'])
            g.db = sqlite3.connect(
                db_file,
                detect_types=sqlite3.PARSE_DECLTYPES
            )
            #g.db.row_factory = sqlite3.Row
            g.db.row_factory = dict_factory
            init_db(g.db)
        except:
            abort(500, "No database found, please sync first.")

    return g.db


def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


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


def get_item_by_id(item_id):
    """ Get the single item from the database with the given id.
    :param item_id:
    :return:
    """
    db = get_db()
    params = {
        "id": item_id,
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
    if len(entries) > 0:
        return entries[0]
    return []


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


def get_statistics(node_titles):
    """ Returns the numbers of all items and all read items
    :param node_titles:
    :return:
    """
    db = get_db()
    counts = []
    for i in ["OR (webferea <> '')", ""]:
        query = f"""
            SELECT count(node.title) AS count
            FROM items 
            JOIN node ON node.node_id = items.node_id
            WHERE 
                node.title IN ('{"', '".join(node_titles)}')
                AND items.comment = 0 
                AND (
                    (items.read = 0 AND items.marked = 0) 
                    {i} 
                )
            ORDER BY items.date DESC
        """
        cur = db.execute(query)
        entries = cur.fetchall()
        counts.append(entries[0]["count"])

    return counts
