#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
@File    : dianping.py
@Author  : qloo
@Version : v1.0
@Time    : 2019-04-10 11:41:22
@History :
@Desc    : 
"""

import copy
import json
import time

from scrapy.http import Request, FormRequest
from scrapy.selector import Selector
from scrapy.spiders import Spider

from hello_spidery.items.parsed_item import ParsedItem
from hello_spidery.downloadermiddlewares.keyword_filter import KeywordCheckScopeEnum, \
    KeywordCheckMethodEnum
from hello_spidery.utils.dianping_css_crack import DianPingCssCracker


class DianPingShop(Spider):
    name = 'dian_ping_shop'

    custom_settings = {
        'COOKIES_ENABLED': True,
        'DOWNLOAD_DELAY': 1,

        'USE_DEFAULT_ERROR_BACK': True,
        # 'KEYWORD_FILTER': [
        #     {
        #         'keyword': 'verify.meituan.com',
        #         'check_method': KeywordCheckMethodEnum.IN_CHECKING,
        #         'check_scope': KeywordCheckScopeEnum.URL,
        #         'allow': False,
        #         'change_proxy': True,
        #     },
        # ]
    }

    dp_cracker = DianPingCssCracker()

    header_home = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en,zh-CN;q=0.9,zh;q=0.8',
        'Connection': 'keep-alive',
        'Host': 'm.dianping.com',
        'Upgrade-Insecure-Requests': '1',
    }

    header_json = {
        'Accept': '*/*',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en,zh-CN;q=0.9,zh;q=0.8',
        'Connection': 'keep-alive',
        'Content-Type': 'application/json',
        'Host': 'm.dianping.com',
        'Origin': 'https://m.dianping.com',
        'Referer': 'https://m.dianping.com/chengdu/ch10/d1?from=m_nav_1_meishi'
    }

    cookie_dict = {
        'PHOENIX_ID': '0a492559-16a05472dbd-2a942c5',
        '_hc.v': '99569c40-c179-176f-e8fa-85bda8642a7e.1554860870',
        '_lxsdk': '16a04ee0a50c8-0246bb646bbc4-71236530-5717a-16a04ee0a51c8',
        '_tr.s': '9C2Ar2QhQb8O8Lgs',
        '_tr.u': 'lBybfMJgaqYxRzfy',
        'cityid': '2',
        'cy': '8',
        'default_ab': 'citylist%3AA%3A1%7Cshop%3AA%3A1%7Cindex%3AA%3A1%7CshopList%3AA%3A1',
        'dp_pwa_v_': '1672865b011de2e1f16a640b5af838452230dcb0',
        'logan_custom_report': '',
        # 'logan_session_token': 'gq9g0zrlrxmys5rypb2p',
        'lxsdk_cuid': '16a04ee0a50c8-0246bb646bbc4-71236530-5717a-16a04ee0a51c8',
        'm_flash2': '1',
        'source': 'm_browser_test_22',
        'switchcityflashtoast': '1',
        'tg_vg': '405214400'
    }

    shop_id_set = set()
    post_data = {
        "pageEnName": "shopList",
        "moduleInfoList": [{"moduleName": "mapiSearch", "query": {"search": {"start": 20, "categoryId": "10",
                            "parentCategoryId": 10, "locateCityid": 0, "limit": 20, "sortId": "0", "cityId": 8,
                            "range": "-1", "maptype": 0, "keyword": ""}}}]}

    def start_requests(self):
        # yield Request('https://m.dianping.com/', headers=self.header_home, dont_filter=True)
        url = 'https://m.dianping.com/isoapi/module'
        form_data = copy.deepcopy(self.post_data)
        # 变换 categoryId  cityId regionId start 以抓取更多数据
        form_data['moduleInfoList'][0]['query']['search']['keyword'] = '烤肉'
        form_data = json.dumps(form_data)
        yield Request(url, method='POST', headers=self.header_json, callback=self.parse_list, body=form_data)

    def get_detail_shop(self, response):
        ck = copy.deepcopy(self.cookie_dict)
        ck['_hc.v'] = f'99569c40-c179-176f-e8fa-85bda8642a7e.{int(time.time())}'
        yield Request('https://m.dianping.com/shop/124991284', callback=self.get_css, cookies=ck)

    def get_css(self, response):
        if 'verify.meituan.com' in response.url:
            return self.update_cookies()

        new_html = self.dp_cracker.crack(response.text)
        slt = Selector(text=new_html)
        print(''.join(slt.xpath('//text()').extract()))
        if self.shop_id_set:
            shop_id = self.shop_id_set.pop()
            ck = copy.deepcopy(self.cookie_dict)
            ck['_hc.v'] = f'99569c40-c179-176f-e8fa-85bda8642a7e.{int(time.time())}'
            yield Request(f'https://m.dianping.com/shop/{shop_id}', callback=self.get_css, cookies=ck)

    def update_cookies(self):
        # return Request()
        pass

    def parse_list(self, response):
        data_dict = json.loads(response.text)
        for item in data_dict['data']['moduleInfoList'][0]['moduleData']['data']['listData']['list']:
            shop_id = item['shopId']
            self.shop_id_set.add(shop_id)
        if not self.shop_id_set:
            return
        shop_id = self.shop_id_set.pop()
        ck = copy.deepcopy(self.cookie_dict)
        ck['_hc.v'] = f'99569c40-c179-176f-e8fa-85bda8642a7e.{int(time.time())}'
        yield Request(f'https://m.dianping.com/shop/{shop_id}', callback=self.get_css, cookies=ck)
