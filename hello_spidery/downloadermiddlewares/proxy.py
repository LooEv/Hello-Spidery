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

import re
import logging

from scrapy.exceptions import NotConfigured
from scrapy.core.downloader.handlers.http11 import TunnelError
from twisted.internet import defer
from twisted.internet.error import TimeoutError, DNSLookupError, \
    ConnectionRefusedError, ConnectionDone, ConnectError, \
    ConnectionLost, TCPTimedOutError
from twisted.web.client import ResponseFailed

from hello_spidery.utils.proxy import ProxyManager

PROXY_IP_MATCH = re.compile(r'(\d+\.\d+\.\d+\.\d+):\d+$')

logger = logging.getLogger(__name__)


class CustomHttpProxyMiddleware:
    EXCEPTIONS_TO_CHANGE_PROXY = (defer.TimeoutError, TimeoutError, DNSLookupError,
                                  ConnectionRefusedError, ConnectionDone, ConnectError,
                                  ConnectionLost, TCPTimedOutError, ResponseFailed,
                                  IOError, TunnelError)

    def __init__(self, use_proxy=False, proxy_manager_config=None):
        if use_proxy and proxy_manager_config is not None:
            self.proxy_mgr = ProxyManager.from_config(proxy_manager_config)
        elif use_proxy and proxy_manager_config is None:
            raise ValueError('if using proxy, PROXY_MANAGER_CONFIG must provide!')
        else:
            self.proxy_mgr = None

    @classmethod
    def from_crawler(cls, crawler):
        if not crawler.settings.getbool('HTTPPROXY_ENABLED'):
            raise NotConfigured
        proxy_manager_config = crawler.settings.getdict('PROXY_MANAGER_CONFIG')
        use_proxy = crawler.settings.getbool('USE_PROXY')
        return cls(use_proxy, proxy_manager_config)

    def change_proxy(self, request):
        proxy = self.proxy_mgr.get_proxy()
        request.meta['proxy'] = proxy.proxy
        logger.info(f'Using proxy: {proxy.proxy}')
        return request

    def update_proxy_status(self, proxy, response_state_code, remove_ip=False):
        if not proxy:
            return
        ip = PROXY_IP_MATCH.search(proxy).group(1)
        self.proxy_mgr.update_proxy_pool(ip, response_state_code, remove_ip=remove_ip)

    def process_exception(self, request, exception, spider):
        if isinstance(exception, self.EXCEPTIONS_TO_CHANGE_PROXY):
            dont_retry = request.meta.get('dont_retry')
            use_proxy = spider.settings.getbool('USE_PROXY')
            if not dont_retry and use_proxy:
                # 808: proxy connect error
                proxy = request.meta.get('proxy')
                logger.info(f'removing proxy: {proxy}')
                self.update_proxy_status(proxy, 808, remove_ip=True)

    def process_request(self, request, spider):
        if spider.settings.getbool('USE_PROXY'):
            if request.meta.get('change_proxy') or request.meta.get('proxy') is None:
                self.change_proxy(request)

    def process_response(self, request, response, spider):
        if spider.settings.getbool('USE_PROXY'):
            if response.status == 200:
                remove_ip = False
            else:
                remove_ip = True
            proxy = request.meta.get('proxy')
            self.update_proxy_status(proxy, response.status, remove_ip=remove_ip)
        return response
