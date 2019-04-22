#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
@File    : sqlite_pipeline.py
@Author  : qloo
@Version : v1.0
@Time    : 2019-04-18 21:17:50
@History :
@Desc    : 
"""

import sqlite3

from contextlib import suppress
from pathlib import Path


class SqlitePipeline:

    def __init__(self, database, timeout, create_db_sql, insert_sql):
        default_database = (Path(__file__).parent.parent / 'data' / 'spider_data.sqlite').absolute()
        self.database = database or str(default_database)
        self.timeout = timeout
        assert create_db_sql is not None and insert_sql is not None
        self.create_db_sql = create_db_sql
        self.insert_sql = insert_sql

    @classmethod
    def from_crawler(cls, crawler):
        settings = crawler.settings
        return cls(
            database=settings.get('SQLITE_DATABASE'),
            timeout=settings.get('SQLITE_CONN_TIMEOUT', 10),
            create_db_sql=settings.get('CREATE_TABLE_SQL_4_SQLITE'),
            insert_sql=settings.get('INSERT_SQL_4_SQLITE')
        )

    def open_spider(self, spider):
        Path(self.database).parent.mkdir(exist_ok=True)
        self.conn = sqlite3.connect(self.database, timeout=self.timeout)
        self.cursor = self.conn.cursor()
        self.cursor.execute(self.create_db_sql)

    def close_spider(self, spider):
        with suppress(AttributeError):
            self.conn.close()

    def process_item(self, item, spider):
        save_data_list = []
        for mbr in item['data']:
            # mbr['_parsed_data'] is a OrderedDict
            save_data_list.append(list(mbr['_parsed_data'].values()))
            if len(save_data_list) > 60:
                self.cursor.executemany(self.insert_sql, save_data_list)
                self.conn.commit()
                save_data_list.clear()
        if save_data_list:
            self.cursor.executemany(self.insert_sql, save_data_list)
            self.conn.commit()
            save_data_list.clear()
        return item
