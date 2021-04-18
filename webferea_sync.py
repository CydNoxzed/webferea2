#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sqlite3
import logging
import argparse
import bz2

import requests


class WebfereaSync:

    COMPRESSIONS = ["bz2"]

    def __init__(self) -> None:
        self.target = ''
        self.username = ''
        self.password = ''
        self.local_database = ''
        self.temp_database = ''
        self.scheme = ''
        self.compression = None

    def run(self):
        self.parse_args()

        try:
            logging.info("Download...")
            self.download()
            logging.info("Merge...")
            self.merge()
            logging.info("Upload...")
            self.upload()
        except requests.exceptions.ConnectionError:
            logging.critical(f"Connection to [{self.target}] failed")
            exit(1)

    def download(self):
        url = self.get_url(download=True)
        resp = requests.get(url, data={}, auth=(self.username, self.password))
        if resp.status_code in [401]:
            logging.error("Authentication failed. Abort. Are password and username correct?")
            exit(1)
        elif resp.status_code in [400]:
            logging.error(f"Bad request: [{resp.content}]")
            exit(1)
        elif resp.status_code != 200:
            logging.error(f"Unknown error. Response Code is not 200. [{resp.content}]")
            exit(1)

        with open(self.temp_database, 'wb') as f:
            data = self.decompress(resp.content)
            f.write(data)

        if not self.is_sqlite3_file(self.temp_database):
            logging.error("Downloaded file is not a valid sqlite3 file. Abort.")
            self.delete_temp_file()
            exit(1)

    def merge(self):
        webitems = self.get_all_changed_webitems(self.temp_database)
        if webitems:
            self.update_local_items(self.local_database, webitems)
        else:
            logging.debug("merge: no items to sync found")

    def upload(self):
        if not self.is_sqlite3_file(self.local_database):
            logging.error("Database to upload is not a valid sqlite3 file. Abort.")
            exit(1)

        # copy and compress
        with open(self.local_database, 'rb') as infile:
            data = self.compress(infile.read())
            with open(self.temp_database, 'wb') as zipped:
                zipped.write(data)

        url = self.get_url(upload=True)
        files = {'database': open(self.temp_database, 'rb')}
        resp = requests.post(url, files=files, auth=(self.username, self.password))

        if resp.status_code in [400]:
            logging.error("No valid database was send. Abort.")
            exit(1)
        if resp.status_code != 200:
            logging.error(f"Unknown error. Response Code is not 200. [{resp.content}]")
            exit(1)

    def delete_temp_file(self):
        if os.path.exists(self.temp_database):
            os.remove(self.temp_database)

    def compress(self, data):
        if not self.compression:
            return data
        if self.compression == 'bz2':
            return bz2.compress(data, compresslevel=9)

    def decompress(self, data):
        if not self.compression:
            return data
        if self.compression == 'bz2':
            return bz2.decompress(data)

    def get_all_changed_webitems(self, db):
        connection = sqlite3.connect(db)
        connection.row_factory = self.dict_factory
        cursor = connection.cursor()

        query = '''SELECT * FROM items WHERE webferea <> '' '''
        try:
            cursor.execute(query)
            webitems = cursor.fetchall()
            return webitems
        except:
            return False

    def update_local_items(self, local_db, webitems):

        logging.debug(f"update_local_items: local_db [{local_db}]")

        connection = sqlite3.connect(local_db)
        connection.row_factory = self.dict_factory
        cursor = connection.cursor()

        for webitem in webitems:

            # get the current local item state
            query = '''SELECT *	FROM items WHERE item_id = "%s" ''' % webitem["item_id"]
            cursor.execute(query)
            localitem = cursor.fetchall()

            # check if something was found
            if not localitem:
                continue

            localitem = localitem[0]

            merge = self.merge_flags_for_items(webitem, localitem)
            merge["item_id"] = webitem["item_id"]

            query = '''
                UPDATE items 
                SET read = :read,
                    marked = :marked
                WHERE item_id = :item_id
                '''
            cursor.execute(query, merge)

        connection.commit()

    def merge_flags_for_items(self, webitem, localitem):
        merge = {
            "read": 0,
            "marked": 0
        }
        if webitem["read"] or localitem["read"]:
            merge["read"] = 1
        if webitem["marked"] or localitem["marked"]:
            merge["marked"] = 1
        return merge

    def dict_factory(self, cursor, row):
        d = {}
        for idx, col in enumerate(cursor.description):
            d[col[0]] = row[idx]
        return d

    def is_sqlite3_file(self, filepath) -> bool:
        """ Check if the sqlite3file is valid
        credits to: http://stackoverflow.com/questions/12932607/
        :param filepath
        :return: True|False
        """
        if not os.path.isfile(filepath):
            return False
        if os.path.getsize(filepath) < 100:  # SQLite database file header is 100 bytes
            return False
        with open(filepath, 'rb') as fd:
            header = fd.read(16)
            fd.seek(0)
            if header == b'SQLite format 3\000':
                return True
        return False

    def get_url(self, upload=False, download=False):
        way = 'upload' if upload else 'download'
        compression = self.compression if self.compression else ''
        return f"{self.scheme}://{self.target}/sync/{way}/{compression}"

    def parse_args(self):
        parser = argparse.ArgumentParser(
            description="Sync the liferea.db with a webferea instance.",
            epilog="examples: webferea_sync.py example.org username passphrase"
        )
        parser.add_argument(
            'target',
            help="http target address of the sync",
        )
        parser.add_argument(
            'user',
            help="username for the http basicauth",
        )
        parser.add_argument(
            'password',
            help="password for the http basicauth",
        )
        parser.add_argument(
            '-d',
            dest="sqlite",
            help="filepath to the liferea.db (default: ~/.local/share/liferea/liferea.db)",
            default="~/.local/share/liferea/liferea.db"
        )
        parser.add_argument(
            '-t',
            dest="tempfilepath",
            help="filepath to the temporary download location for the yet to merged liferea.db (default: /tmp/webferea_liferea.db)",
            default="/tmp/webferea_liferea.db"
        )
        parser.add_argument(
            '-s',
            dest="scheme",
            help="name of the scheme (default: https)",
            default="https"
        )
        parser.add_argument(
            '-c',
            dest="compression",
            help=f"transfer compression (default: none)",
            choices=self.COMPRESSIONS,
            default=None
        )
        parser.add_argument(
            '-q', '--quiet',
            dest="quiet",
            help="Only output errors.",
            action=argparse.BooleanOptionalAction,
            default=False
        )
        parser.add_argument(
            '-v', '--verbose',
            dest="verbose",
            help="Show debug outputs",
            action=argparse.BooleanOptionalAction,
            default=False
        )
        args = parser.parse_args()

        self.target = args.target
        self.username = args.user
        self.password = args.password
        self.local_database = os.path.expanduser(args.sqlite)
        self.temp_database = os.path.expanduser(args.tempfilepath)
        self.scheme = args.scheme
        self.compression = args.compression

        level = logging.INFO
        if args.quiet:
            level = logging.ERROR
        if args.verbose:
            level = logging.DEBUG
        logging.basicConfig(level=level)


if __name__ == "__main__":
    webferea_sync = WebfereaSync()
    webferea_sync.run()
