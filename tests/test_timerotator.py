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
    print(tmpfile)
    item_lbls = []
    for i in range(0, 5):
        lbl = f"Item_{i}"
        item_lbls.append(lbl)
        rotator.add_item(lbl)

    for i in range(0, 25):
        row = rotator.get_oldest(update_ts=True)
        lbl = item_lbls[i % len(item_lbls)]
        assert row['label'] == lbl

    rotator.close()


    # Test context ("with _ as _ :")
    for i in range(0, 25):
        lbl = item_lbls[i % len(item_lbls)]
        with tr.timerotator.TimeRotater(tmpfile) as rotator:
            item = rotator.get_oldest(update_ts=True)
            assert item['label'] == lbl

    for i in range(0, 25):
        lbl = item_lbls[i % len(item_lbls)]
        with tr.timerotator.TimeRotater(tmpfile) as rotator:
            item = rotator.get_oldest(update_ts=True)
            assert item['label'] == lbl


    # Test get_by_key
    rotator = tr.timerotator.TimeRotater(tmpfile)

    row1 = rotator.get_by_key(5, update_ts=True)
    time.sleep(0.1)
    row2 = rotator.get_by_key(5, update_ts=False)
    time.sleep(0.1)
    row3 = rotator.get_by_key(5, update_ts=True)

    row4 = rotator.get_by_key("Item_4")

    assert  row1['label'] == "Item_4" and row2['label'] == "Item_4"
    assert row1['time'] < row2['time']
    assert row2['time'] == row3['time']
    assert row4['label'] == row3['label']
    ##################################################################
    # Test __iter__
    ##################################################################
    rotator = tr.timerotator.TimeRotater(tmpfile)
    t0 = datetime.datetime.now() - datetime.timedelta(hours=1)
    for row in rotator:
        dt = row['time']
        assert dt > t0
        t0 = dt

    # Test .items()

    t0 = datetime.datetime.now() - datetime.timedelta(hours=1)
    for row in rotator.items():
        dt = row['time']
        assert dt > t0
        t0 = dt

    t0 = datetime.datetime.now() + datetime.timedelta(hours=1)
    for row in rotator.items(ascending=False):
        dt = row['time']
        assert dt < t0
        t0 = dt

    # Test __contains__
    assert "Item_0" in rotator
    assert not "ASDF" in rotator
    assert rotator.get_by_key(1)['label'] == "Item_0"

    # Test __delitem__
    del rotator["Item_0"]
    assert not "Item_0" in rotator
    failed = False
    try:
        del rotator["Item_123"]
    except KeyError:
        failed = True
    assert failed
