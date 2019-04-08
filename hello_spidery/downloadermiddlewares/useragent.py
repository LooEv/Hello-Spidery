#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
@File    : useragent.py
@Author  : qloo
@Version : v1.0
@Time    : 2019-04-04 18:56:20
@History :
@Desc    :
"""

import random

from faker import Faker
from scrapy.downloadermiddlewares.useragent import UserAgentMiddleware

__all__ = ["CustomUserAgentMiddleware"]


class CustomUserAgentMiddleware(UserAgentMiddleware):
    def __init__(self, user_agent=None):
        if isinstance(user_agent, str) and 'scrapy' in user_agent.lower():
            user_agent = ''
        super().__init__(user_agent)
        self.fake = Faker()
        browsers_list = ['chrome', 'firefox', 'safari'] * 5
        self.user_agent_list = [getattr(self.fake, browser)() for browser in browsers_list]

    def process_request(self, request, spider):
        request.headers.setdefault(
            b'User-Agent', self.user_agent or random.choice(self.user_agent_list)
        )
