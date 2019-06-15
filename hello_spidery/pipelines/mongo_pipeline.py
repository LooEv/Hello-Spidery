#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
@File    : mongo_pipeline.py
@Author  : qloo
@Version : v1.0
@Time    : 2019-03-28 23:17:50
@History :
@Desc    : 
"""

import pymongo

from contextlib import suppress


class MongoPipeline:

    def __init__(self, mongo_uri, mongo_db, batch_size_4_save_data):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db
        self.batch_size_4_save_data = batch_size_4_save_data
        self.data_list = []

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=crawler.settings.get('MONGO_URI', '127.0.0.1:27017'),
            mongo_db=crawler.settings.get('MONGO_DATABASE', 'items'),
            batch_size_4_save_data=crawler.settings.getint('BATCH_SIZE_4_SAVE_DATA', 20)
        )

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]

    def close_spider(self, spider):
        if self.data_list:
            self.db[spider.name].insert_many(self.data_list)
        with suppress(AttributeError):
            self.client.close()

    def process_item(self, item, spider):
        for mbr in item['data']:
            self.data_list.append(mbr['_parsed_data'])
            if len(self.data_list) >= self.batch_size_4_save_data:
                self.db[spider.name].insert_many(self.data_list)
                self.data_list.clear()
        return item
