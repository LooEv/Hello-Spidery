#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
@File    : proxy.py
@Author  : qloo
@Version : v1.0
@Time    : 2019-04-08 23:11:36
@History :
@Desc    : 
"""

from scrapy.downloadermiddlewares.httpproxy import HttpProxyMiddleware

from hello_spidery.utils.proxy import ProxyManager


class CustomHttpProxyMiddleware(HttpProxyMiddleware):
    def __init__(self, auth_encoding='latin-1'):
        super().__init__(auth_encoding)
        self.proxy_mgr = ProxyManager()

    # TODO  request meta change_proxy
