#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
@File    : biu.py
@Author  : qloo
@Version : v1.0
@Time    : 2019-03-31 22:20:09
@History :
@Desc    : 
"""
import time

import requests
from hello_spidery.spiders.waimai import MeituanEncryptor

header = {
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Accept-Encoding": "gzip, deflate",
    "Accept-Language": "en,zh-CN;q=0.9,zh;q=0.8",
    "Connection": "keep-alive",
    # "Content-Length": "329",
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    "Cookie": 'w_utmz="utm_campaign=(direct)&utm_source=(direct)&utm_medium=(none)&utm_content=(none)&utm_term=(none)"; w_uuid=c5k9hpvZNj2Zrx-Mm7vujZQI2yfQqRNEAeBhB-hp7jkWr5dRna6jpV5S4g9HwtKp; waddrname="%E5%9B%9B%E5%B7%9D%E7%8E%B0%E4%BB%A3%E8%81%8C%E4%B8%9A%E5%AD%A6%E9%99%A2"; w_geoid=wm3vwstbsr47; w_cid=510122; w_cpy=shuangliuxian; w_cpy_cn="%E5%8F%8C%E6%B5%81%E5%8C%BA"; w_ah="30.522889997810125,104.004663862288,%E5%9B%9B%E5%B7%9D%E7%8E%B0%E4%BB%A3%E8%81%8C%E4%B8%9A%E5%AD%A6%E9%99%A2"; w_visitid=0e0c9af3-e7e6-44dd-ae6f-8224240e0f22; wm_order_channel=default; au_trace_key_net=default; _lx_utm=utm_source%3D60066; _lxsdk_cuid=169d3f7e288c8-0c4b43f7ef6e4b-2a792346-7a102-169d3f7e289c8; _lxsdk=169d3f7e288c8-0c4b43f7ef6e4b-2a792346-7a102-169d3f7e289c8; openh5_uuid=169d3f7e288c8-0c4b43f7ef6e4b-2a792346-7a102-169d3f7e289c8; uuid=169d3f7e288c8-0c4b43f7ef6e4b-2a792346-7a102-169d3f7e289c8; _ga=GA1.3.1307048299.1554040569; _gid=GA1.3.267856865.1554040569; __mta=249846329.1554040571312.1554040571312.1554040571312.1; ci=59; rvct=59; JSESSIONID=54nba39ziorarmoeqp9ix99y; _gat=1; _lxsdk_s=169d3f7d9f4-44e-a66-3ac%7C%7C36',
    "Host": "waimai.meituan.com",
    "Origin": "http://waimai.meituan.com",
    "Referer": "http://waimai.meituan.com/home/wm3vwstbsr47",
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.75 Safari/537.36",
    "X-FOR-WITH": "uzkyoAqixQxZZKNJXQ9mEvKO9n0WrOxnFpCENq3gM2/UgIHKgjVmynavvaNUWT+BoQAJu5aC+aDnkHFdF/qqH2S0A4Pcd6MV725NAv18Us0O3P2j9yqaEc3EK4jhEijMT7W2iGf0pTlmhZGcKTDo1Q==",
    "X-Requested-With": "XMLHttpRequest",
}

post_data = {
    "classify_type": "cate_all",
    "sort_type": "0",
    "price_type": "0",
    "support_online_pay": "0",
    "support_invoice": "0",
    "support_logistic": "0",
    "page_offset": "41",
    "page_size": "20",
    "mtsi_font_css_version": "20ad699b",
    "uuid": "c5k9hpvZNj2Zrx-Mm7vujZQI2yfQqRNEAeBhB-hp7jkWr5dRna6jpV5S4g9HwtKp",
    "platform": "1",
    "partner": "4",
    "originUrl": "http://waimai.meituan.com/",
}

url = 'http://waimai.meituan.com/ajax/poilist?_token=%s'
encryptor = MeituanEncryptor(post_data, 'http://waimai.meituan.com/home/wm3vwstbsr47', round(time.time() * 1000))

token = encryptor.get_token()
req = requests.post(url % token, data=post_data, headers=header)
print(req.text)
