#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
@File    : parsed_data_pipeline.py
@Author  : qloo
@Version : v1.0
@Time    : 2019-03-28 22:16:20
@History :
@Desc    : 
"""


class ParsedDataPipeline:

    def process_item(self, item, spider):
        item_dict = dict(item)
        item_dict.update(item_dict.pop('_parsed_data', {}))
        item_dict.pop("_dup_str", "")
        return item_dict
