# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class BaseItem(scrapy.Item):
    _id = scrapy.Field()
    update_time = scrapy.Field()
    do_time = scrapy.Field()
    version = scrapy.Field()

    _html = scrapy.Field()
    _request_url = scrapy.Field()
    _request_method = scrapy.Field()
    _request_params = scrapy.Field()

    _job_id = scrapy.Field()
    _parent_job_id = scrapy.Field()

    _dup_str = scrapy.Field()
