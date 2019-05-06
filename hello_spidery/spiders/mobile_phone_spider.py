#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
@File    : mobile_phone_spider.py
@Author  : qloo
@Version : v1.0
@Time    : 2019-04-21 18:48:13
@History :
@Desc    :
"""

import re
import time

import maya

from collections import OrderedDict
from urllib.parse import urlparse

from scrapy.http import Request
from scrapy.spiders import Rule
from scrapy.linkextractors import LinkExtractor

from hello_spidery.utils.commons import seconds_2_str
from hello_spidery.utils.spiders.crawl_spider import HelloCrawlSpider
from hello_spidery.utils.selector_utils import xpath_extract_all_text_strip, \
    xpath_extract_all_text_no_spaces as xpath_text_no_spaces

LOCAL_TIMEZONE = str(maya.get_localzone())


class MobilePhoneSpider(HelloCrawlSpider):
    name = 'mobile_phone'

    custom_settings = {
        'USE_DEFAULT_ERROR_BACK': True,
        'DOWNLOAD_DELAY': 1,
        'USE_PROXY': True,

        # DATABASE
        'SQLITE_DATABASE': '',
        'CREATE_TABLE_SQL_4_SQLITE': """CREATE TABLE IF NOT EXISTS spider_data
                                        (`mobile_phone_number`  char(11) NOT NULL primary key,
                                         `url`                  varchar(100) NOT NULL,
                                         `crawl_time`           varchar(19) NOT NULL,
                                         `timestamp`            integer   NOT NULL);""",
        'INSERT_SQL_4_SQLITE': """INSERT OR REPLACE INTO spider_data VALUES (?,?,?,?);"""
    }

    start_urls = [
        'https://www.pdflibr.com/?page=1',
        'https://yunduanxin.net/China-Phone-Number/',
        # 'http://www.smszk.com/',
        # 'http://www.z-sms.com/',
        # 'https://www.becmd.com/',
        # 'https://www.receivingsms.com/'
    ]

    url_and_phone_number_mapping = {}

    phone_num_match = re.compile(r'\d{11,}')

    list_page_xpaths = {
        'www.pdflibr.com': {
            'phone_number': '//div[contains(@class, "number-list-flag")]//h3',
            'a_tag': '//div[contains(@class, "sms-number-read")]//a/@href'
        },
        'yunduanxin.net': {
            'phone_number_and_url': '//a[text()="接收短信"]/@href'
        },
        'www.smszk.com': {
            'phone_number_and_url': '//a[text()="查看短信"]/@href'
        },
        'www.receivingsms.com': {
            'phone_number_and_url': '//a[text()="接收短信"]/@href'
        },
        'www.becmd.com': {
            'phone_number_and_url': '//a[text()="阅读短信"]/@href'
        }
    }

    database_column_list = ['mobile_phone_number', 'url', 'crawl_time', 'timestamp']

    rules = (
        Rule(LinkExtractor(allow=r'www\.pdflibr\.com/\?page=\d+', allow_domains='www.pdflibr.com'),
             callback='parse_list', follow=True),

        Rule(LinkExtractor(allow=r'yunduanxin\.net/China-Phone-Number/?', allow_domains='yunduanxin.net'),
             callback='parse_list', follow=True),

        Rule(LinkExtractor(allow=r'www\.smszk\.com/?$', allow_domains='www.smszk.com'),
             callback='parse_list', follow=True),

        Rule(LinkExtractor(allow=r'www\.receivingsms\.com/?$', allow_domains='www.receivingsms.com'),
             callback='parse_list', follow=True),

        Rule(LinkExtractor(allow=r'www\.becmd\.com/?$', allow_domains='www.becmd.com'),
             callback='parse_list', follow=True),
    )

    parse_detail_page_method = {
        'www.pdflibr.com': 'parse_pdflibr',
        'yunduanxin.net': 'parse_yunduanxin',
    }

    def get_ph_num(self, ph_num_text):
        _ph_num = self.phone_num_match.search(ph_num_text)
        if not _ph_num:
            return
        _ph_num = _ph_num.group()[-11:]
        return _ph_num

    def parse_list(self, response):
        host_name = urlparse(response.url).hostname
        xpaths_dict = self.list_page_xpaths.get(host_name, {})
        if not xpaths_dict:
            return

        if 'phone_number_and_url' in xpaths_dict:
            href_list = [mbr for mbr in response.xpath(xpaths_dict['phone_number_and_url']).extract()]
            phone_number_list = href_list[:]
        else:
            phone_number_selectors = response.xpath(xpaths_dict['phone_number'])
            phone_number_list = [xpath_text_no_spaces(mbr) for mbr in phone_number_selectors]
            href_list = [mbr for mbr in response.xpath(xpaths_dict['a_tag']).extract()]

        for ph_num, href in zip(phone_number_list, href_list):
            _ph_num = self.get_ph_num(ph_num)
            if not _ph_num:
                continue
            if int(_ph_num[:2]) < 13 or int(_ph_num[:2]) >= 20:
                continue
            url = response.urljoin(href)
            if url not in self.url_and_phone_number_mapping:
                self.url_and_phone_number_mapping[url] = _ph_num
                yield Request(url, callback=self.parse_detail)

    def parse_detail(self, response):
        host_name = urlparse(response.url).hostname
        parse_method_name = self.parse_detail_page_method.get(host_name)
        if not parse_method_name:
            self.logger.warn(f'wrong url request {response.url}')
            return

        parse_method = getattr(self, parse_method_name, None)
        if callable(parse_method):
            for item in parse_method(response):
                yield item

    def parse_pdflibr(self, response):
        table = response.xpath('(//table[@class="table table-hover"])[last()]')
        table_headers = [xpath_text_no_spaces(th) for th in table.xpath('.//th')]
        mobile_phone_number = self.url_and_phone_number_mapping[response.url]
        trs = table.xpath('tbody//tr')
        if not trs:
            self.logger.warning(f"invalid phone number url: {response.url}")
            return
        try:
            values = [xpath_extract_all_text_strip(td) for td in trs[0].xpath('.//td')]
            a_dict = dict(zip(table_headers[1:], values[1:]))
            msg_received_time = maya.when(a_dict['发送日期'], timezone=LOCAL_TIMEZONE).epoch
            now_timestamp = maya.now().epoch
            if now_timestamp - msg_received_time > 2 * 60 * 60:
                self.logger.warning(f"nobody use phone number url: {response.url}")
            else:
                item = self.assemble_parsed_item(response)
                a_dict = {
                    'mobile_phone_number': mobile_phone_number,
                    'url': response.url,
                    'crawl_time': seconds_2_str(),
                    'timestamp': int(time.time()),
                }
                item['_parsed_data'] = self.assemble_result(a_dict)
                yield item
        except Exception:
            self.logger.warning(f'fail to parse url: {response.url}')

    def parse_yunduanxin(self, response):
        item_xpath = '//div[contains(@class, "row border-bottom table-hover")]'
        headers = ['电话号码', '发送日期', '短信内容']
        mobile_phone_number = self.url_and_phone_number_mapping[response.url]
        divs = response.xpath(item_xpath)
        if not divs:
            self.logger.warning(f"invalid phone number url: {response.url}")
            return
        try:
            values = [xpath_extract_all_text_strip(_div) for _div in divs[0].xpath('./div')]
            from_where = values[0]
            values[0] = from_where[:from_where.find('From')].strip()
            a_dict = dict(zip(headers, values))
            msg_received_time = maya.when(a_dict['发送日期'], timezone=LOCAL_TIMEZONE).epoch
            now_timestamp = maya.now().epoch
            if now_timestamp - msg_received_time > 2 * 60 * 60:
                self.logger.warning(f"nobody use phone number url: {response.url}")
            else:
                item = self.assemble_parsed_item(response)
                a_dict = {
                    'mobile_phone_number': mobile_phone_number,
                    'url': response.url,
                    'crawl_time': seconds_2_str(),
                    'timestamp': int(time.time()),
                }
                item['_parsed_data'] = self.assemble_result(a_dict)
                yield item
        except Exception:
            self.logger.warning(f'fail to parse url: {response.url}')

    def assemble_result(self, a_dict):
        result_dict = OrderedDict()
        for col in self.database_column_list:
            result_dict[col] = a_dict[col]
        return result_dict
