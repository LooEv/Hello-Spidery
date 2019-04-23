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

from scrapy.exceptions import NotConfigured

from hello_spidery.utils.proxy import ProxyManager


class CustomHttpProxyMiddleware:
    def __init__(self, proxy_manager_config):
        self.proxy_mgr = ProxyManager.from_config(proxy_manager_config)

    @classmethod
    def from_crawler(cls, crawler):
        if not crawler.settings.getbool('HTTPPROXY_ENABLED'):
            raise NotConfigured
        proxy_manager_config = crawler.settings.get('PROXY_MANAGER_CONFIG')
        return cls(proxy_manager_config)

    def process_request(self, request, spider):
        if request.meta.get('change_proxy'):
            proxy = self.proxy_mgr.get_proxy()
            request.meta['proxy'] = proxy.proxy
        elif spider.settings.getbool('USE_PROXY') and request.meta.get('proxy') is None:
            proxy = self.proxy_mgr.get_proxy()
            request.meta['proxy'] = proxy.proxy
