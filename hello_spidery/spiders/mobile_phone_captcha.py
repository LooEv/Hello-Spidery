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
import time

from scrapy.http import Request, FormRequest
from scrapy.selector import Selector
from scrapy.spiders import Spider

from hello_spidery.items.parse_item import ParsedItem
from hello_spidery.downloadermiddlewares.keyword_filter import KeywordCheckScopeEnum, \
    KeywordCheckMethodEnum
from hello_spidery.utils.dianping_css_crack import DianPingCssCracker


class MobilePhoneCaptcha(Spider):
    name = 'mobile_phone_captcha'

    custom_settings = {
        'USE_DEFAULT_ERROR_BACK': True,
    }

    start_urls = [
        'https://www.pdflibr.com/',
        'https://yunduanxin.net/China-Phone-Number/',
        'http://www.smszk.com/',
        'http://www.z-sms.com/',
        'https://www.becmd.com/',
        'https://www.receivingsms.com/'
    ]

    def parse(self, response):
        pass
