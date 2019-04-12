#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
@File    : selector_utils.py
@Author  : qloo
@Version : v1.0
@Time    : 2019-04-12 14:04:57
@History :
@Desc    : 
"""
from scrapy.selector import Selector


def xpath_extract_all_text(slt: Selector, xpath: str = '.'):
    if not xpath.endswith('//text()'):
        xpath += '//text()'
    return ''.join(slt.xpath(xpath).extract())
