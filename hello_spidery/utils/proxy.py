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

from hello_spidery.utils.commons import seconds_2_str


@attr.s
class Proxy:
    ip = attr.ib()
    port = attr.ib(validator=int)
    create_time = attr.ib()
    state = attr.ib(default=200)
    user = attr.ib(default=None)
    pwd = attr.ib(default=None)
    used_times = attr.ib(default=0)
    expired_time = attr.ib(default=None)

    @property
    def proxy(self):
        if self.user:
            return f'{self.user}:{self.pwd}@{self.ip}:{self.port}'
        else:
            return f'{self.ip}:{self.port}'


class ProxyManager:
    def __init__(self, config: dict):
        self._proxy_server_url = config['proxy_server_url']
        self._proxy_pool_size = config.get('proxy_pool_size', 10)
        self._proxy_pool = {}

    def get_proxy(self):
        pass

    def update_proxy(self, ip, last_state_code=200):
        if ip in self._proxy_pool:
            proxy = self._proxy_pool[ip]
            proxy.state = last_state_code
            proxy.used_times += 1
        else:
            # TODO add some logs
            pass

    def _prepare_request_data(self):
        pass

    @staticmethod
    def make_data_2_proxy(data):
        ip, port = data.split(':')
        proxy = Proxy(ip, port, create_time=seconds_2_str())
        return proxy

    @classmethod
    def from_config(cls, config: dict):
        return cls(config)
