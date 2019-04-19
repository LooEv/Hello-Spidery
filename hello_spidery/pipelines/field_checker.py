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

from jsonschema.validators import Draft7Validator
from scrapy.exceptions import DropItem


class FieldCheckerPipeline:
    def __init__(self, fields_json_schema):
        self.validator = Draft7Validator(fields_json_schema)

    @classmethod
    def from_settings(cls, settings):
        return cls(settings.get('FIELDS_JSON_SCHEMA', {}))

    def process_item(self, item, spider):
        item_dict = dict(item)
        try:
            self.validator.validate(item_dict)
        except Exception as e:
            raise DropItem(f'invalid item: {e.message}')
        return item
