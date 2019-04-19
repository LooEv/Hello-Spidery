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

import re


def clean_all_spaces(string_or_list):
    """
        Remove all spaces(including unicode spaces) in the given string

        :param string_or_list: a unicode string or list of string to be removed spaces in it
        :returns: a string without spaces
    """
    s = ''.join(string_or_list) if isinstance(string_or_list, list) else string_or_list
    return re.sub(r'\s+', '', s, flags=re.UNICODE)


def xpath_first(slt, xpath):
    """
    Get first item extracted from slt by xpath.

    :param slt: an instance of =scrapy.selector.Selector=
    :param xpath: a string of xpath syntax
    :returns: a string result of the selector or ''(if slt select nothing)
    """
    first_item = slt.xpath(xpath).extract_first()

    return first_item if first_item else ''


def css_first(slt, css):
    """
    Get first item extracted from slt by css.

    :param slt: an instance of =scrapy.selector.Selector=
    :param css: a string of css syntax
    :returns: a string result of the selector or ''(if slt select nothing)
    """
    first_item = slt.css(css).extract_first()

    return first_item if first_item else ''


def xpath_first_text(slt, xpath='.', chars=None):
    """
    Get first item's stripped text(by appending '/text()' after xpath) extracted from slt.

    :param slt: an instance of =scrapy.selector.Selector=
    :param xpath: a string of xpath syntax
    :param chars: a string of chars passed to string.strip()
    :returns: a string result of the selector or ''(if slt select nothing)
    """
    return xpath_first(slt, xpath + '/text()').strip(chars)


def css_first_text(slt, css='', chars=None):
    """
    Get first item's stripped text(by appending '::text'('/text()' for xpath) after css) extracted from slt.

    :param slt: an instance of =scrapy.selector.Selector=
    :param css: a string of css syntax
    :param chars: a string of chars passed to string.strip()
    :returns: a string result of the selector or ''(if slt select nothing)
    """
    return css_first(slt, css + '::text').strip(chars)


def css_first_text_no_spaces(slt, css=''):
    """
    Get all text in first item(by appending '::text' after css) with all spaces removed

    :param slt: an instance of =scrapy.selector.Selector=
    :param css: a string of css syntax
    :returns: a string result of the selector or ''(if slt select nothing)
    """
    return clean_all_spaces(css_first(slt, css + '::text'))


def css_re_first(slt, css, regex):
    """
    Get first item extracted from slt by regular expression.

    :param slt: an instance of =scrapy.selector.Selector=
    :param css: a string of css syntax
    :param regex: a string of regular expression syntax
    :returns: a string result of the selector or ''(if slt select nothing)
    """
    first_item = slt.css(css).re_first(regex)

    return first_item if first_item else ''


def xpath_re_first(slt, xpath, regex):
    """
    Get first item extracted from slt by regular expression.

    :param slt: an instance of =scrapy.selector.Selector=
    :param xpath: a string of xpath syntax
    :param regex: a string of regular expression syntax
    :returns: a string result of the selector or ''(if slt select nothing)
    """
    first_item = slt.xpath(xpath).re_first(regex)

    return first_item if first_item else ''


def css_extract(slt, css):
    """
    Extract items from scrapy Selector by css

    :param slt: an instance of =scrapy.selector.Selector=
    :param css: a string of css syntax
    :returns: list of strings or [](if the css hits nothing)
    """
    return slt.css(css).extract()


def xpath_extract(slt, xpath):
    """
    Extract items from scrapy Selector by xpath

    :param slt: an instance of =scrapy.selector.Selector=
    :param xpath: a string of xpath syntax
    :returns: list of strings or [](if the xpath hits nothing)
    """
    return slt.xpath(xpath).extract()


def xpath_extract_all_text(slt, xpath='.'):
    """
    Join all text from scrapy Selector by xpath

    :param slt: an instance of =scrapy.selector.Selector=
    :param xpath: a string of xpath syntax without '//text()'
    :returns: a string of all nodes' text
    """
    return ''.join(slt.xpath(xpath + '//text()').extract())


def xpath_extract_all_text_strip(slt, xpath='.'):
    """
    Join all text from scrapy Selector by xpath and strip it

    :param slt: an instance of =scrapy.selector.Selector=
    :param xpath: a string of xpath syntax without '//text()'
    :returns: a string of all nodes' text
    """
    return xpath_extract_all_text(slt, xpath).strip()


def xpath_extract_all_text_no_spaces(slt, xpath='.'):
    """
    Join all text from scrapy Selector by xpath without spaces

    :param slt: an instance of =scrapy.selector.Selector=
    :param xpath: a string of xpath syntax without '//text()'
    :returns: a string of all nodes' text but without spaces
    """
    return clean_all_spaces(xpath_extract_all_text(slt, xpath))
