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
from scrapy.exceptions import NotConfigured

from hello_spidery.utils.proxy import ProxyManager


class CustomHttpProxyMiddleware(HttpProxyMiddleware):
    def __init__(self, proxy_manager_config, auth_encoding='latin-1'):
        super().__init__(auth_encoding)
        self.proxy_mgr = ProxyManager.from_config(proxy_manager_config)

    @classmethod
    def from_crawler(cls, crawler):
        if not crawler.settings.getbool('HTTPPROXY_ENABLED'):
            raise NotConfigured
        auth_encoding = crawler.settings.get('HTTPPROXY_AUTH_ENCODING')
        proxy_manager_config = crawler.settings.get('PROXY_MANAGER_CONFIG')
        return cls(proxy_manager_config, auth_encoding)
    # TODO  request meta change_proxy
