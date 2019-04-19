#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
@File    : multi_parsed_item_assemble.py
@Author  : qloo
@Version : v1.0
@Time    : 2019-04-19 13:33:40
@History :
@Desc    : 
"""

from hello_spidery.items.parsed_item import ParsedItem
from hello_spidery.items.multi_parsed_item import MultiParsedItem


class MultiParsedItemAssemblerMiddleware:
    def process_spider_output(self, response, result, spider):
        items = []
        for x in result:
            if isinstance(x, ParsedItem):
                items.append(x)
            else:
                yield x
        if items:
            yield MultiParsedItem(data=items)
