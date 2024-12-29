#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on 2024-12-28T18:11:34-05:00

@author: nate
"""

import timerotator as tr
import tempfile
import time

def test_time_rotator():
    tmpfile = tempfile.mktemp(".tr")
    rotator = tr.timerotator.TimeRotater(tmpfile)

    item_lbls = []
    for i in range(0, 5):
        lbl = f"Item_{i}"
        item_lbls.append(lbl)
        rotator.add_item(lbl)

    for i in range(0, 25):
        row = rotator.get_oldest()
        lbl = item_lbls[i % len(item_lbls)]
        assert row[2] == lbl

    rotator.close()


    for i in range(0, 25):
        lbl = item_lbls[i % len(item_lbls)]
        with tr.timerotator.TimeRotater(tmpfile) as rotator:
            (ent_id, ent_ts, ent_lbl) = rotator.get_oldest()
            assert ent_lbl == lbl
