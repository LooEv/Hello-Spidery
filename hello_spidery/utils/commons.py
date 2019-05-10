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

import hashlib
import re
import time


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


def cookie_str_2_dict(text: str):
    """
    you can copy cookie string from browser and parse it to a dict
    :param text:
    :return:
    """
    if not text.endswith(';'):
        text += ';'
    result = re.findall(r'(.+?)=(.*?);\s?', text)
    return dict(result)


def header_str_2_dict(text: str):
    """
    you can copy headers string from browser and parse it to a dict
    :param text:
    :return:
    """
    header = {}
    for line in text.splitlines():
        if not line.strip():
            continue
        key, value = line.split(':', 1)
        header[key.strip()] = value.strip()
    return header
