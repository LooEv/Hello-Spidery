#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
@File    : duplicates_pipeline.py
@Author  : qloo
@Version : v1.0
@Time    : 2019-04-15 22:47:37
@History :
@Desc    : 
"""

from scrapy.exceptions import DropItem

from hello_spidery.utils.commons import calc_str_md5
from hello_spidery.items.multi_parsed_item import MultiParsedItem


class DuplicatesPipeline:

    def __init__(self):
        self.items_seen = set()

    def process_item(self, item, spider):
        if isinstance(item, MultiParsedItem):
            items_list = []
            for mbr in item['data']:
                dup_str = mbr.get('_dup_str', mbr['_id'])
                dup_str_md5 = calc_str_md5(dup_str)
                if dup_str_md5 in self.items_seen:
                    # TODO add some log
                    continue
                else:
                    self.items_seen.add(dup_str_md5)
                    items_list.append(mbr)
            if items_list:
                return MultiParsedItem(data=items_list)
            else:
                raise DropItem("Duplicate item found: %s" % item)

        else:
            dup_str = item.get('_dup_str', item['_id'])
            dup_str_md5 = calc_str_md5(dup_str)

            if dup_str_md5 in self.items_seen:
                raise DropItem("Duplicate item found: %s" % item)
            else:
                self.items_seen.add(dup_str_md5)
                return item
