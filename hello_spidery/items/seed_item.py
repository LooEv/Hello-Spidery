#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
@File    : seed_item.py
@Author  : qloo
@Version : v1.0
@Time    : 2019-03-30 08:49:26
@History :
@Desc    : 
"""
import scrapy

from .base_item import BaseItem


class SeedItem(BaseItem):
    seed_data = scrapy.Field()
    _extra_data = scrapy.Field()  # the extra data what need to pass to next spider
