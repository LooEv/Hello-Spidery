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

    def __init__(self, database, timeout):
        self.database = database
        self.timeout = timeout
        self.conn = None
        self.cursor = None

    @classmethod
    def from_crawler(cls, crawler):
        settings = crawler.settings
        default_database = (Path(__file__).parent.parent / 'data' / 'spider_data.db').absolute()
        return cls(
            database=settings.get('SQLITE_DATABASE', str(default_database)),
            timeout=settings.get('SQLITE_CONN_TIMEOUT', 10)
        )

    def open_spider(self, spider):
        self.conn = sqlite3.connect(self.database, timeout=self.timeout)
        self.cursor = self.conn.cursor()
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS spider_data
               (`ID` integer primary key AUTOINCREMENT,
               `FROM`          varchar (100)   NOT NULL,
               `DATE`          varchar (50)    NOT NULL,
               `MESSAGE`       TEXT NOT NULL);''')

    def close_spider(self, spider):
        with suppress(AttributeError):
            self.conn.close()

    def process_item(self, item, spider):
        parsed_data = item['_parsed_data']
        save_data = parsed_data['电话号码'], parsed_data['发送日期'], parsed_data['短信内容']
        self.cursor.execute("INSERT INTO spider_data (`FROM`,`DATE`,MESSAGE) VALUES (?,?,?)", save_data)
        self.conn.commit()
        return item
