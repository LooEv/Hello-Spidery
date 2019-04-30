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
import traceback

from urllib.parse import urljoin
from scrapy.selector import Selector


@attr.s
class DianPingCssCracker:
    raw_html = attr.ib(default=None)
    shop_url = attr.ib(default='https://m.dianping.com/shop/23314835')
    cls_prefix_svg_mapping_dict = attr.ib(default=attr.Factory(dict))
    cls_prefix_px_mapping_dict = attr.ib(default=attr.Factory(dict))
    cls_text_mapping_dict = attr.ib(default=attr.Factory(dict))

    svg_url_match = re.compile(r'span\[class\^="(\w+?)"\].+?url\((//.+?svgtextcss/.+?\.svg)')
    class_attr_match = re.compile(r'\.(\w+){background:-?(.+?)px\s*-?(.+?)px;}')
    font_size_match = re.compile(r'font-size:\s*(\d+)px')
    span_match = re.compile(r'(<span\s*class="(.+?)"></span>)')

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
            class_prefix_list = []
            svg_url_set = set()
            for class_prefix, svg_url in self.svg_url_match.findall(resp.text):
                svg_url = urljoin(self.shop_url, svg_url)
                class_prefix_list.append(class_prefix)
                self.cls_prefix_svg_mapping_dict[class_prefix] = svg_url
                svg_url_set.add(svg_url)

            for cls, x, y in self.class_attr_match.findall(resp.text):
                a_tuple = (cls, int(float(x)), int(float(y)))
                if cls[:1] in class_prefix_list:
                    class_prefix = cls[:1]
                elif cls[:2] in class_prefix_list:
                    class_prefix = cls[:2]
                elif cls[:3] in class_prefix_list:
                    class_prefix = cls[:3]
                else:
                    class_prefix = cls[:4]
                self.cls_prefix_px_mapping_dict.setdefault(class_prefix, []).append(a_tuple)
            return svg_url_set
        except Exception:
            # self.logger.exception('fail to get svg url: ')
            traceback.print_exc()

    def fetch_svg_resp(self, svg_url):
        resp = requests.get(svg_url, headers=self.header)
        return resp.text

    def parse_svg_resp(self, html, cls_pixel_list):
        font_size = int(self.font_size_match.search(html).group(1))
        if 'path id=' in html:
            return self._parse_svg_resp_1(html, font_size, cls_pixel_list)
        else:
            return self._parse_svg_resp_2(html, font_size, cls_pixel_list)

    def _parse_svg_resp_1(self, html, font_size, cls_pixel_list):
        path_id_y_match = re.compile(r'path\s*id="(\d+)"\s*d="M0\s*(\d+)\s*H600"')
        path_id_y_list = [(int(item[-1]), item[0]) for item in path_id_y_match.findall(html)]
        path_id_y_list.sort(key=lambda _x: _x[0])

        font_list_match = re.compile(r'xlink:href="#(\d+)".+?>(.+?)<', re.IGNORECASE)
        path_id_font_list_mapping_dict = dict(font_list_match.findall(html))
        cls_text_list = []
        for cls, x, y in cls_pixel_list:
            for _y, path_id in path_id_y_list:
                if y <= _y:
                    index = int(x / font_size)
                    font_list = path_id_font_list_mapping_dict[path_id]
                    cls_text_list.append((cls, font_list[index]))
                    break
        return cls_text_list

    def _parse_svg_resp_2(self, html, font_size, cls_pixel_list):
        font_list_match = re.compile(r'y="(\d+)">(.+?)<', re.IGNORECASE)
        y_and_font_list = [(int(item[0]), item[-1]) for item in font_list_match.findall(html)]
        y_and_font_list.sort(key=lambda _x: _x[0])
        cls_text_list = []
        for cls, x, y in cls_pixel_list:
            for _y, font_list in y_and_font_list:
                if y <= _y:
                    index = int(x / font_size)
                    cls_text_list.append((cls, font_list[index]))
                    break
        return cls_text_list

    def get_cls_prefix_by_svg_url(self, svg_url):
        for cls_prefix, _svg_url in self.cls_prefix_svg_mapping_dict.items():
            if _svg_url == svg_url:
                return cls_prefix

    def replace_raw_html(self, css_url):
        cls_text_mapping_dict = self.cls_text_mapping_dict[css_url]
        for span, cls in self.span_match.findall(self.raw_html):
            if cls not in cls_text_mapping_dict:
                continue
            self.raw_html = self.raw_html.replace(span, cls_text_mapping_dict[cls])
        return self.raw_html

    def crack(self, raw_html=None):
        if raw_html is not None:
            self.raw_html = raw_html
        else:
            raise ValueError('get wrong html')

        css_url = self.get_css_url()
        if css_url not in self.cls_text_mapping_dict:
            cls_text_mapping_dict = {}
            for svg_url in self.get_svg_url(css_url):
                svg_html = self.fetch_svg_resp(svg_url)
                cls_prefix = self.get_cls_prefix_by_svg_url(svg_url)
                cls_pixel_list = self.cls_prefix_px_mapping_dict[cls_prefix]
                cls_text_list = self.parse_svg_resp(svg_html, cls_pixel_list)
                cls_text_mapping_dict.update(dict(cls_text_list))
            self.cls_text_mapping_dict[css_url] = cls_text_mapping_dict
        return self.replace_raw_html(css_url)
