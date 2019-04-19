# -*- coding: utf-8 -*-

# Scrapy settings for hello_spidery project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://doc.scrapy.org/en/latest/topics/settings.html
#     https://doc.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://doc.scrapy.org/en/latest/topics/spider-middleware.html

BOT_NAME = 'hello_spidery'

SPIDER_MODULES = ['hello_spidery.spiders']
NEWSPIDER_MODULE = 'hello_spidery.spiders'


# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'hello_spidery (+http://www.yourdomain.com)'

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

RETRY_TIMES = 2

# Configure maximum concurrent requests performed by Scrapy (default: 16)
#CONCURRENT_REQUESTS = 32

# Configure a delay for requests for the same website (default: 0)
# See https://doc.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
#DOWNLOAD_DELAY = 3
# The download delay setting will honor only one of:
#CONCURRENT_REQUESTS_PER_DOMAIN = 16
#CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
#TELNETCONSOLE_ENABLED = False

# Override the default request headers:
#DEFAULT_REQUEST_HEADERS = {
#   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
#   'Accept-Language': 'en',
#}

# Enable or disable spider downloadermiddlewares
# See https://doc.scrapy.org/en/latest/topics/spider-middleware.html
SPIDER_MIDDLEWARES = {
    'hello_spidery.spidermiddlewares.multi_parsed_item_assemble.MultiParsedItemAssemblerMiddleware': 900,
}

# KEYWORD_FILTER = [
#     {
#         'keyword': 'test',
#         'check_method': 0,
#         'check_scope': 0,
#         'allow': False,
#         'change_proxy': True,
#     },
# ]

FIELDS_JSON_SCHEMA = {
    "type": "object",
    "properties": {
        "_id": {"type": "string"},
        "update_time": {"type": "number"},
        "do_time": {"type": "string"},
        "version": {"type": "string"},
        "_parsed_data": {"type": "object"},
        "_dup_str": {"type": "string"},

        "_html": {"type": "string"},
        "_request_url": {"type": "string"},
        "_request_method": {"type": "string"},
        "_request_params": {"type": "string"},
        "_job_id": {"type": "integer"},
        "_parent_job_id": {"type": "integer"},
    },
    "required": [
        "_id", "update_time", "do_time", "version", '_parsed_data',
        "_html", "_request_url", "_request_method", "_request_params"
    ],
    "additionalProperties": False,
}


# Enable or disable downloader middlewares
# See https://doc.scrapy.org/en/latest/topics/downloader-middleware.html
DOWNLOADER_MIDDLEWARES = {
    'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
    'hello_spidery.downloadermiddlewares.default_error_back.DefaultErrorBack': 1,
    'hello_spidery.downloadermiddlewares.useragent.CustomUserAgentMiddleware': 500,
    'hello_spidery.downloadermiddlewares.add_cookie.GiveSomeCookies': 580,
    # must before RedirectMiddleware and after HttpCompressionMiddleware
    'hello_spidery.downloadermiddlewares.keyword_filter.KeywordFilterMiddleware': 585,
}

# Enable or disable extensions
# See https://doc.scrapy.org/en/latest/topics/extensions.html
#EXTENSIONS = {
#    'scrapy.extensions.telnet.TelnetConsole': None,
#}

# Configure item pipelines
# See https://doc.scrapy.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
    # 'hello_spidery.pipelines.mongo_pipeline.MongoPipeline': 800,
    'hello_spidery.pipelines.duplicates_pipeline.DuplicatesPipeline': 300,
    # 'hello_spidery.pipelines.field_checker.FieldCheckerPipeline': 400,
    'hello_spidery.pipelines.sqlite_pipeline.SqlitePipeline': 500,
    'hello_spidery.pipelines.parsed_data_pipeline.ParsedDataPipeline': 600,
}

# Enable and configure the AutoThrottle extension (disabled by default)
# See https://doc.scrapy.org/en/latest/topics/autothrottle.html
#AUTOTHROTTLE_ENABLED = True
# The initial download delay
#AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
#AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
#AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
#AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See https://doc.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
#HTTPCACHE_ENABLED = True
#HTTPCACHE_EXPIRATION_SECS = 0
#HTTPCACHE_DIR = 'httpcache'
#HTTPCACHE_IGNORE_HTTP_CODES = []
#HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'


############ DATABASE #################
SQLITE_DATABASE = ''
CREATE_TABLE_SQL_4_SQLITE = """CREATE TABLE IF NOT EXISTS spider_data
                                   (`id` integer primary key AUTOINCREMENT,
                                   `from`          varchar (100)   NOT NULL,
                                   `date`          varchar (50)    NOT NULL,
                                   `message`       TEXT NOT NULL);"""
INSERT_SQL_4_SQLITE = """INSERT INTO spider_data (`from`,`date`,message) VALUES (?,?,?)"""
