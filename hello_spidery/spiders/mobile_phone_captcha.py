#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
@File    : mobile_phone_captcha.py
@Author  : qloo
@Version : v1.0
@Time    : 2019-04-11 18:48:13
@History :
@Desc    : 
"""

import copy
import json
import re
import time
from urllib.parse import urlparse

from scrapy.http import Request, FormRequest
from scrapy.selector import Selector
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor

from hello_spidery.items.parse_item import ParsedItem
from hello_spidery.utils.selector_utils import xpath_extract_all_text


class MobilePhoneCaptcha(CrawlSpider):
    name = 'mobile_phone_captcha'

    custom_settings = {
        'USE_DEFAULT_ERROR_BACK': True,
        'DOWNLOAD_DELAY': 1,
    }

    start_urls = [
        'https://www.pdflibr.com/?page=1',
        # 'https://yunduanxin.net/China-Phone-Number/',
        # 'http://www.smszk.com/',
        # 'http://www.z-sms.com/',
        # 'https://www.becmd.com/',
        # 'https://www.receivingsms.com/'
    ]

    phone_number_and_url_mapping = {}

    phone_num_match = re.compile(r'\d{11,}')

    list_page_xpaths = {
        'www.pdflibr.com': {
            'phone_number': '//div[contains(@class, "number-list-flag")]//h3',
            'a_tag': '//div[contains(@class, "sms-number-read")]//a/@href'
        },
        'yunduanxin.net': {
            'phone_number_and_url': '//a[text()="接收短信"]/@href'
        }
    }

    parse_detail_page_method = {
        'www.pdflibr.com': 'parse_pdflibr',
        'yunduanxin.net': 'parse_yunduanxin',
    }

    rules = (
        Rule(LinkExtractor(allow=r'www\.pdflibr\.com/\?page=\d+', allow_domains='www.pdflibr.com'),
             callback='parse_list', follow=True),
        Rule(LinkExtractor(allow=r'/SMSContent/\d+$'), callback='parse_detail', follow=True),
        Rule(LinkExtractor(allow=r'/SMSContent/\d+\?page=[2]$'), callback='parse_detail'),

        Rule(LinkExtractor(allow=r'yunduanxin\.net/China-Phone-Number/', allow_domains='yunduanxin.net'),
             callback='parse_list', follow=True, process_links='process_url'),
        Rule(LinkExtractor(allow=r'/info/\d+/'), callback='parse_detail'),
    )

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
            phone_number_list = [xpath_extract_all_text(mbr) for mbr in phone_number_selectors]
            href_list = [mbr for mbr in response.xpath(xpaths_dict['a_tag']).extract()]

        for ph_num, href in zip(phone_number_list, href_list):
            _ph_num = self.get_ph_num(ph_num)
            if not _ph_num:
                continue
            url = response.urljoin(href)
            self.phone_number_and_url_mapping[_ph_num] = url

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
        table_headers = [xpath_extract_all_text(th) for th in table.xpath('.//th')]
        for tr in table.xpath('tbody//tr'):
            values = [xpath_extract_all_text(td) for td in tr.xpath('.//td')]
            print(dict(zip(table_headers[1:], values[1:])))
        yield

    def parse_yunduanxin(self, response):
        item_xpath = '//div[contains(@class, "row border-bottom table-hover")]'
        for div in response.xpath(item_xpath):
            values = [xpath_extract_all_text(_div) for _div in div.xpath('./div')]
