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
    cls_prefix_svg_mapping_dict = attr.ib(default=attr.Factory(dict))
    css_url_list = attr.ib(default=attr.Factory(list))
    cls_prefix_px_mapping_dict = attr.ib(default=attr.Factory(dict))
    cls_num_mapping_dict = attr.ib(default=attr.Factory(dict))

    svg_url_match = re.compile(r'span\[class\^="(\w+?)"\].+?url\((//.+?svgtextcss/.+?\.svg)')
    class_attr_match = re.compile(r'\.(\w+){background:(.+?)px\s*(.+?)px;}')

    header = {
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) Chrome/73.0.3683.75 Safari/537.36'
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
            for cls, x, y in self.class_attr_match.findall(resp.text):
                self.cls_prefix_px_mapping_dict.setdefault(cls[:3], []).append((cls, float(x), float(y)))

            for cls_pixel_list in self.cls_prefix_px_mapping_dict.values():
                cls_pixel_list.sort(key=lambda x: x[1])

            for class_prefix, svg_url in self.svg_url_match.findall(resp.text):
                svg_url = urljoin(self.shop_url, svg_url)
                self.cls_prefix_svg_mapping_dict[class_prefix] = svg_url
                yield svg_url
        except Exception:
            # self.logger.exception('fail to get svg url: ')
            pass

    def fetch_svg_resp(self, svg_url):
        resp = requests.get(svg_url, headers=self.header)
        return resp.text

    def parse_svg_resp(self, html, cls_pixel_list):
        font_list = re.findall(r'<text.*?y="(.*?)">(.*?)<', html)
        if len(cls_pixel_list) == len(font_list[0][-1]):
            for cls, number in zip(cls_pixel_list, font_list[0][-1][::-1]):
                self.cls_num_mapping_dict[cls[0]] = number

    def get_cls_prefix_by_svg_url(self, svg_url):
        for cls_prefix, _svg_url in self.cls_prefix_svg_mapping_dict.items():
            if _svg_url == svg_url:
                return cls_prefix

    def crack(self, raw_html=None):
        if raw_html is not None:
            self.raw_html = raw_html
        elif raw_html is None and self.raw_html is None:
            raise ValueError('get wrong html')
        css_url = self.get_css_url()
        if css_url in self.css_url_list:
            return

        for svg_url in self.get_svg_url(css_url):
            svg_html = self.fetch_svg_resp(svg_url)
            cls_prefix = self.get_cls_prefix_by_svg_url(svg_url)
            cls_pixel_list = self.cls_prefix_px_mapping_dict[cls_prefix]
            self.parse_svg_resp(svg_html, cls_pixel_list)


if __name__ == '__main__':
    from html_dp import html

    dp = DianPingCssCracker(raw_html=html)
    dp.crack()
