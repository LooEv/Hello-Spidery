#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
@File    : seed_provider.py
@Author  : qloo
@Version : v1.0
@Time    : 2019-05-12 22:33:50
@History :
@Desc    :
"""

import pymongo


class BaseSeedProvider:

    def get_seed(self, seed_suffix=None):
        raise NotImplementedError


class RedisSeedProvider(BaseSeedProvider):
    pass


class SSDBSeedProvider(BaseSeedProvider):
    pass


class MongoDBSeedProvider(BaseSeedProvider):
    def __init__(self, host, port, db_name, seed_queue_name,
                 seed_suffix_list=None, **kwargs):
        self.mongo_uri = f'{host}:{port}'
        self.server = pymongo.MongoClient(self.mongo_uri)
        self.seed_queue_name = seed_queue_name
        self.db = self.server.get_database(db_name)
        self.seed_suffix_list = seed_suffix_list or []

    def get_seed(self, seed_suffix=None):
        seed_queue_name = self.handle_seed_queue_name(seed_suffix)
        seed = self.db.get_collection(seed_queue_name).find_one(max_time_ms=5000)
        if seed:
            self.db.get_collection(seed_queue_name).delete_one({'_id': seed['_id']})
        return seed

    def handle_seed_queue_name(self, seed_suffix=None):
        if seed_suffix is not None:
            seed_queue_name = self.seed_queue_name + seed_suffix
        else:
            seed_queue_name = self.seed_queue_name
        return seed_queue_name

    def is_empty(self, seed_suffix=None):
        seed_queue_name = self.handle_seed_queue_name(seed_suffix)
        return self.db.get_collection(seed_queue_name).count() == 0

    def close(self):
        self.server.close()


SEED_PROVIDER_CLASS_MAPPING = {
    'redis': RedisSeedProvider,
    'ssdb': SSDBSeedProvider,
    'mongodb': MongoDBSeedProvider
}


class SeedProvider:
    @classmethod
    def from_config(cls, **kwargs):
        seed_server_type = kwargs.pop('seed_server_type')
        assert seed_server_type in SEED_PROVIDER_CLASS_MAPPING
        seed_provider_cls = SEED_PROVIDER_CLASS_MAPPING[seed_server_type]
        return seed_provider_cls(**kwargs)
