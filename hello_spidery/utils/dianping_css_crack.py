#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
@File    : dianping_css_crack.py
@Author  : qloo
@Version : v1.0
@Time    : 2019-04-10 17:43:31
@History :
@Desc    : 
"""

import attr
import requests
import re

from urllib.parse import urljoin
from scrapy.selector import Selector


@attr.s
class DianPingCssCracker:
    raw_html = attr.ib(default=None)
    shop_url = attr.ib(default='https://m.dianping.com/shop/23314835')
    css_svg_mapping_dict = attr.ib(default=attr.Factory(dict))
    css_url_list = attr.ib(default=attr.Factory(list))

    svg_url_match = re.compile(r'url\(//(.+?svgtextcss/.+?\.svg)')

    header = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en,zh-CN;q=0.9,zh;q=0.8',
        'Connection': 'keep-alive',
        'Host': 'm.dianping.com',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/70.0.3538.102 Safari/537.36',
    }

    def get_css_url(self):
        text_css_xpath = '//link[contains(@href, "svgtextcss")]/@href'
        slt = Selector(text=self.raw_html)
        css_url = slt.xpath(text_css_xpath).extract_first()
        css_url = urljoin(self.shop_url, css_url)
        return css_url

    def get_svg_url(self, css_url):
        try:
            resp = requests.get(css_url, headers=self.header)
            for svg_url in self.svg_url_match.findall(resp.text):
                svg_url = urljoin(self.shop_url, svg_url)
                yield svg_url
        except Exception:
            # self.logger.exception('fail to get svg url: ')
            pass

    def fetch_svg_resp(self, svg_url):
        resp = requests.get(svg_url, headers=self.header)
        return resp.text

    def parse_svg_resp(self, html):
        font_list = re.findall(r'<text.*?y="(.*?)">(.*?)<', html)

    def crack(self, raw_html=None):
        if raw_html is not None:
            self.raw_html = raw_html
        else:
            raise ValueError('get wrong html')
        css_url = self.get_css_url()
        if css_url in self.css_url_list:
            return

        for svg_url in self.get_svg_url(css_url):
            svg_resp = self.fetch_svg_resp(svg_url)
