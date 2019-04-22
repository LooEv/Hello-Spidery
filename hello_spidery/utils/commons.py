#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
@File    : commons.py
@Author  : qloo
@Version : v1.0
@Time    : 2019-04-16 22:15:32
@History :
@Desc    : 
"""

import time
import hashlib


def calc_str_md5(strings: str, encoding='utf-8'):
    md5_obj = hashlib.md5()
    md5_obj.update(strings.encode(encoding=encoding))
    return md5_obj.hexdigest()


def seconds_2_str(str_format="%Y-%m-%d %H:%M:%S", seconds=None):
    if seconds is None:
        seconds = time.time()
    t_tuple = time.localtime(seconds)
    return time.strftime(str_format, t_tuple)


def str_2_seconds(time_str, str_format="%Y-%m-%d %H:%M:%S"):
    return time.mktime(time.strptime(time_str, str_format))


def map_fields(original_dict, fields_mapping_dict):
    if not isinstance(original_dict, dict):
        raise TypeError('except a dict to map the fields')

    temp_dict = {}
    for key, value in original_dict.items():
        temp_dict[fields_mapping_dict.get(key, key)] = value
    return temp_dict
