#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
@File    : parsed_item.py
@Author  : qloo
@Version : v1.0
@Time    : 2019-03-28 22:06:50
@History :
@Desc    : 
"""

import scrapy

from .base_item import BaseItem


class ParsedItem(BaseItem):
    _parsed_data = scrapy.Field()
