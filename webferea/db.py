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


def get_items_by_node_titles(node_titles, decorate=True):
    """ Returns all items which are linked to the given node_title

    :param node_titles:
    :return:
    """

    db = get_db()

    hide_read_snipplet = "OR (webferea <> '')" if session["show_read"] else ""
    node_snipplet = "', '".join(node_titles)

    query = f"""
        SELECT 
            items.*, 
            node.title AS node_title 
        FROM items 
        JOIN node 
            ON node.node_id = items.node_id
        WHERE 
            node.node_id IN (
                SELECT node.node_id
                FROM node
                JOIN node as parent_node
                    ON parent_node.node_id = node.parent_id
                WHERE 
                    node.title IN ('{node_snipplet}')
                    OR parent_node.title IN ('{node_snipplet}')
            )
            AND items.comment = 0 
            AND (( 
                    items.read = 0 
                    AND items.marked = 0 
                ) {hide_read_snipplet} )
            ORDER BY items.date DESC
        """

    cur = db.execute(query)
    entries = cur.fetchall()
    if decorate:
        return decorate_all_with_metadata(entries)
    return entries


def get_item_by_id(item_id, decorate=True):
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
        if decorate:
            return decorate_all_with_metadata(entries)[0]
        return entries[0]
    return []


def decorate_all_with_metadata(entries):
    # use the long version of the entry from the metadata, instead the short version
    for entry in entries:
        metadata = get_metadata_by_item_id(entry['item_id'])

        rich_content = metadata.get("richContent")
        if rich_content:
            entry['description'] = rich_content
        if entry['description'] is None:
            entry['description'] = ''

        author = metadata.get("author")
        if author:
            entry['author'] = author
        if not 'author' in entry or entry['author'] is None:
            creator = metadata.get("creator")
            if creator:
                entry['author'] = creator
        if not 'author' in entry or entry['author'] is None:
            entry['author'] = ''

    return entries


def get_metadata_by_item_id(item_id: int):
    metadata = {}
    db = get_db()
    cur = db.execute(f'''
        SELECT *
        FROM metadata 
        WHERE item_id = {item_id}
        ORDER BY nr ASC
        ''')
    result = cur.fetchall()
    if len(result) > 0:
        for row in result:
            metadata[row["key"]] = row["value"]
    return metadata


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
    node_snipplet = "', '".join(node_titles)
    modes = [
        "AND ( (items.read = 1 OR items.marked = 1) AND (webferea <> '') )",  # read
        "AND (items.read = 0 AND items.marked = 0)",  # unread
        "AND (items.read = 0 AND items.marked = 0) OR (webferea <> '') "  # total, which would be processed by webferea
    ]
    for i in modes:
        query = f"""
            SELECT count(node.title) AS count
            FROM items 
            JOIN node ON node.node_id = items.node_id
            WHERE 
                node.node_id IN (
                    SELECT node.node_id
                    FROM node
                    JOIN node as parent_node
                        ON parent_node.node_id = node.parent_id
                    WHERE 
                        node.title IN ('{node_snipplet}')
                        OR parent_node.title IN ('{node_snipplet}')
                )
                AND items.comment = 0 
                {i} 
            ORDER BY items.date DESC
        """
        cur = db.execute(query)
        entries = cur.fetchall()
        counts.append(entries[0]["count"])

    return counts
