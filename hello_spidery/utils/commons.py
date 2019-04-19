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


def calc_str_md5(strings: str, encoding='utf-8'):
    md5_obj = hashlib.md5()
    md5_obj.update(strings.encode(encoding=encoding))
    return md5_obj.hexdigest()
