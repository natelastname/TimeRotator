#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on 2024-12-28T18:11:34-05:00

@author: nate
"""

import timerotator as tr
import tempfile
import time
import datetime

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
    ##################################################################
    # Test context ("with _ as _ :")
    ##################################################################
    for i in range(0, 25):
        lbl = item_lbls[i % len(item_lbls)]
        with tr.timerotator.TimeRotater(tmpfile) as rotator:
            (ent_id, ent_ts, ent_lbl) = rotator.get_oldest()
            assert ent_lbl == lbl

    for i in range(0, 25):
        lbl = item_lbls[i % len(item_lbls)]
        with tr.timerotator.TimeRotater(tmpfile) as rotator:
            (ent_id, ent_ts, ent_lbl) = rotator.get_oldest()
            assert ent_lbl == lbl

    ##################################################################
    rotator = tr.timerotator.TimeRotater(tmpfile)

    (_, ts1, lbl1) = rotator.get_by_id(5)
    time.sleep(0.1)
    (_, ts2, lbl2) = rotator.get_by_id(5, update_ts=False)
    time.sleep(0.1)
    (_, ts3, lbl3) = rotator.get_by_id(5)

    assert  lbl1 == "Item_4" and lbl2 == "Item_4"
    assert datetime.datetime.fromisoformat(ts1) < datetime.datetime.fromisoformat(ts2)
    assert ts2 == ts3
