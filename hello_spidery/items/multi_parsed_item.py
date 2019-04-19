#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
@File    : multi_parsed_item.py
@Author  : qloo
@Version : v1.0
@Time    : 2019-04-19 12:06:47
@History :
@Desc    : 
"""

import scrapy


class MultiParsedItem(scrapy.Item):
    data = scrapy.Field()
