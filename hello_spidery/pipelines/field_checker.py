#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
@File    : field_checker.py
@Author  : qloo
@Version : v1.0
@Time    : 2019-04-03 08:54:00
@History :
@Desc    : 
"""

import jsonschema


class FieldCheckerPipeline:
    def __init__(self, fields_json_schema):
        self.mongo_db = fields_json_schema

    @classmethod
    def from_settings(cls, settings):
        return cls(settings.get('FIELDS_JSON_SCHEMA', []))

    def process_item(self, item, spider):
        item_dict = dict(item)
        item_dict.update(item_dict.pop('_parsed_data', {}))
        item_dict.pop("_dup_str", "")
        return item_dict
