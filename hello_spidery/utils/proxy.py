#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
@File    : proxy.py
@Author  : qloo
@Version : v1.0
@Time    : 2019-04-08 23:12:49
@History :
@Desc    : 
"""

import attr
import requests

from operator import itemgetter

from hello_spidery.utils.commons import seconds_2_str


@attr.s
class Proxy:
    ip = attr.ib()
    port = attr.ib()
    create_time = attr.ib()
    state = attr.ib(default=200)
    user = attr.ib(default=None)
    pwd = attr.ib(default=None)
    used_times = attr.ib(default=0)
    expired_time = attr.ib(default=None)
    protocol = attr.ib(default='http')

    @property
    def proxy(self):
        if self.user:
            return f'{self.protocol}://{self.user}:{self.pwd}@{self.ip}:{self.port}'
        else:
            return f'{self.protocol}://{self.ip}:{self.port}'


class ProxyManager:
    def __init__(self, config: dict):
        self._proxy_server_url = config['proxy_server_url']
        self._proxy_pool_size = config.get('proxy_pool_size', 10)
        self._proxy_protocol = config.get('proxy_protocol', 'http')
        self._max_used_times = config.get('max_used_times', 10)
        self._proxy_pool = {}

    def get_proxy(self):
        if self._proxy_pool:
            proxy = self._choice_proxy()
            if proxy:
                return proxy

        while 1:
            try:
                response = requests.get(self._proxy_server_url)
                for proxy_dict in response.json():
                    proxy = self.make_data_2_proxy(proxy_dict)
                    self._proxy_pool[proxy.ip] = proxy
                if len(self._proxy_pool) >= self._proxy_pool_size:
                    proxy = self._choice_proxy()
                    return proxy
            except Exception:
                pass

    def _choice_proxy(self):
        sorted_proxy = sorted(list(self._proxy_pool.values()), key=itemgetter('used_times'))
        for proxy in sorted_proxy:
            if proxy.state != 200 or proxy.used_times >= self._max_used_times:
                self._proxy_pool.pop(proxy.ip, None)
            else:
                return proxy

    def update_proxy_pool(self, ip, last_state_code=200, remove_ip=False):
        if remove_ip:
            self._proxy_pool.pop(ip, None)
            return
        if ip in self._proxy_pool:
            proxy = self._proxy_pool[ip]
            proxy.state = last_state_code
            proxy.used_times += 1
        else:
            # TODO add some logs
            pass

    def _prepare_request_data(self):
        pass

    def make_data_2_proxy(self, data):
        ip, port = data['host'], data['port']
        proxy = Proxy(ip, port, create_time=seconds_2_str(), protocol=self._proxy_protocol)
        return proxy

    @classmethod
    def from_config(cls, config: dict):
        return cls(config)
