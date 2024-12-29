#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on 2024-12-28T18:11:34-05:00

@author: nate
"""
#import shelve
#import pydantic
#from pydantic import BaseModel, Field, WithJsonSchema
#from typing import Sequence, Any, Callable, Hashable
import os

import sqlite3
import datetime
import random
import atexit


class TimeRotater:
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
        return self.conn.execute(cmd, vals)

    def _table_exists(self, table):
        cmd = f"""
        SELECT name FROM sqlite_master
        WHERE type='table' AND name="{table}";
        """
        cursor = self.conn.execute(cmd)
        res = cursor.fetchall()
        if len(res) == 0:
            return False
        return True

    def __iter__(self):
        cursor = self.conn.execute("")
        #rows = conn.execute("PRAGMA table_info();")
        desc = [row[0] for row in cursor.description]
        for row in cursor.fetchall():
            yield {key: val for key, val in zip(desc, row)}


    def add_item(self, label: str, dt:datetime.datetime = None):
        if not dt:
            dt = datetime.datetime.now()
        item = {
            "time": datetime.datetime.now(),
            "label": label
        }
        self._insert_into("entries", item)
        self.conn.commit()

    def update_by_id(self, ent_id:int):
        dt = datetime.datetime.now()
        self.conn.execute(f"""
UPDATE entries
SET time = '{dt}'
WHERE id = {ent_id} ;
        """)
        self.conn.commit()
        return

    def get_oldest(self, update_ts=True):
        '''
        Gets the oldest entry)
        '''
        cursor = self.conn.execute("SELECT *, min(time) from entries;")
        result = cursor.fetchall()
        (ent_id, ent_ts, ent_lbl, _) = result[0]
        if not update_ts:
            return result[0]
        self.update_by_id(ent_id)
        return (ent_id, ent_ts, ent_lbl)

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
