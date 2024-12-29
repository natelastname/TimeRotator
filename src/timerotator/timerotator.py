#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on 2024-12-28T18:11:34-05:00

@author: nate
"""

import os
import sqlite3
import datetime
import random
import atexit

class TimeRotater:

    def _iter_cursor(self, cursor):
        desc = [row[0] for row in cursor.description]
        for row in cursor.fetchall():
            val = {key: val for key, val in zip(desc, row)}
            val['time'] = datetime.datetime.fromtimestamp(val['time'])
            yield val

    def _insert_into(self, table: str, item: dict):
        keys = []
        vals = []
        for key, val in item.items():
            keys.append(key)
            if isinstance(val, datetime.datetime):
                val = val.timestamp()
            vals.append(val)
        keys_str = ", ".join(keys)
        vals_str = ", ".join([str(val) for val in vals])
        qmarks = ", ".join(["?" for val in vals])
        cmd = f"INSERT INTO {table}({keys_str}) VALUES({qmarks});"
        res = self.conn.execute(cmd, vals)
        return res.lastrowid

    def _table_exists(self, table):
        cmd = f"""
        SELECT name FROM sqlite_master
        WHERE type='table' AND name=?;
        """
        cursor = self.conn.execute(cmd, table)
        res = cursor.fetchall()
        if len(res) == 0:
            return False
        return True

    def add_item(self, label: str, dt:datetime.datetime = None):
        if not dt:
            dt = datetime.datetime.now()
        item = {
            "time": dt.timestamp(),
            "label": label
        }
        self._insert_into("entries", item)
        self.conn.commit()

    def update_by_label(self, label:str):
        dt = datetime.datetime.now().timestamp()
        self.conn.execute(f"""
UPDATE entries
SET time = '{dt}'
WHERE label = (?) ;
        """, (label,))
        self.conn.commit()
        return

    def update_by_id(self, ent_id:int):
        dt = datetime.datetime.now().timestamp()
        self.conn.execute(f"""
UPDATE entries
SET time = '{dt}'
WHERE id = (?) ;
        """, (ent_id,) )
        self.conn.commit()
        return

    def get_oldest(self, update_ts=False):
        '''
        Gets the oldest entry
        '''
        cursor = self.conn.execute("SELECT *, min(time) from entries;")
        result = next(self._iter_cursor(cursor))
        result.pop('min(time)', None)
        if not update_ts:
            return result
        self.update_by_id(result['id'])
        return result

    def __init__(self, filename):
        self.conn = sqlite3.connect(
            filename,
            detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES
        )
        atexit.register(self.conn.close)
        self.conn.executescript(f"""
CREATE TABLE IF NOT EXISTS entries (
    id INTEGER PRIMARY KEY,
    time DATETIME NOT NULL,
    label TEXT
);
PRAGMA journal_mode=WAL;
PRAGMA optimize;
        """)

    def get_by_label(self, label:str, update_ts=False):
        cursor = self.conn.execute(f"SELECT * FROM entries WHERE label = (?)", (label,) )
        res = None
        for row in self._iter_cursor(cursor):
            res = row
        if not res or not update_ts:
            return res
        self.update_by_id(res['id'])
        return res

    def get_by_id(self, row_id:id, update_ts=False):
        cursor = self.conn.execute(f"SELECT * FROM entries WHERE id = (?)", (row_id,) )
        res = None
        for row in self._iter_cursor(cursor):
            res = row
        if not res or not update_ts:
            return res
        self.update_by_id(res['id'])
        return res

    def __iter__(self):
        pass

    def __enter__(self):
        return self

    def close(self):
        atexit.unregister(self.conn.close)
        self.conn.close()

    def __exit__(self, type, value, traceback):
        self.close()
        return

    def __getitem__(self, key):
        if isinstance(key, str):
            return self.get_by_label(key)
        elif isinstance(key, int):
            return self.get_by_id(key)

        raise KeyError(key)

    def items(self, update_ts=False):
        cursor = self.conn.execute("SELECT * FROM entries ORDER BY time ASC")
        for row in self._iter_cursor(cursor):
            if update_ts:
                self.update_by_id(row['id'])
            yield row

    def __iter__(self):
        for item in self.items(update_ts=False):
            yield item

    def __contains__(self, label: str):
        res = self.get_by_label(label)
        if res:
            return True
        return False
