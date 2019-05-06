#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
@File    : captcha_app.py
@Author  : qloo
@Version : v1.0
@Time    : 2019-04-22 21:26:49
@History :
@Desc    :
"""

import attr
import json
import re
import time
import sqlite3
import traceback

import maya
import tornado.options
import tornado.httpserver
import tornado.ioloop

from collections import deque
from random import choice
from pathlib import Path
from urllib.parse import urlparse, urlencode
from scrapy.selector import Selector
from tzlocal import get_localzone
from tornado import gen
from tornado.httpclient import AsyncHTTPClient
from tornado.web import RequestHandler, Application

from hello_spidery.utils.selector_utils import xpath_extract_all_text_strip, \
    xpath_extract_all_text_no_spaces as xpath_text_no_spaces

# global
ROUTE_LIST = []
TASK_QUEUE = deque(maxlen=1000)
CALL_SERVER_TIMES_QUEUE = deque(maxlen=500)
LOCAL_TIMEZONE = str(get_localzone())
SC_FTPP_URL = 'https://sc.ftqq.com/xxxxxx.send'  # xxxxxx 代表你的 server酱 的 secret key
PARSER_METHOD_MAPPING = {
    'www.pdflibr.com': 'parse_pdflibr',
    'yunduanxin.net': 'parse_yunduanxin',
}
WEIXIN_MSG_TEMPLATE = """####{电话号码} ({发送日期})####\n{短信内容}"""
DEFAULT_DB_FILE_PATH = (Path(__file__).parent.parent / 'hello_spidery' / 'data' / 'spider_data.sqlite').absolute()


def route(path):
    def inner(cls):
        ROUTE_LIST.append((path, cls))
        return cls

    return inner


@attr.s
class CaptchaTask:
    ph_num = attr.ib()
    url = attr.ib()
    server_name = attr.ib()
    ph_num_fetched_time = attr.ib()
    request_times = attr.ib(default=0)


class SqliteDB:
    def __init__(self, db_file_path=None):
        if db_file_path is None:
            db_file_path = str(DEFAULT_DB_FILE_PATH)
        self.conn = sqlite3.connect(db_file_path, timeout=10)
        self.cursor = self.conn.cursor()

    def get_ph_num(self, *args, **kwargs):
        query_result = self.cursor.execute("""select * from spider_data""")
        return query_result

    def del_data(self, data):
        try:
            sql = f"""DELETE FROM spider_data WHERE mobile_phone_number='{data[0]}';"""
            self.cursor.execute(sql)
            self.conn.commit()
        except Exception:
            traceback.print_exc()

    def close(self):
        self.conn.close()


class DatabaseManager:
    def __init__(self, db_instance):
        self.db = db_instance

    def get_data_by_name(self, data_name, *args, **kwargs):
        method = getattr(self.db, 'get_' + data_name, None)
        if callable(method):
            return method(*args, **kwargs)
        else:
            raise AttributeError('called wrong method name')


class Parser:
    http_client = AsyncHTTPClient()
    header = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'accept-encoding': 'gzip, deflate',
        'accept-language': 'en,zh-CN;q=0.9,zh;q=0.8',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64 Chrome/70.0.3538.102 Safari/537.36'
    }

    @staticmethod
    @gen.coroutine
    def get_response(url):
        resp = yield Parser.http_client.fetch(url, headers=Parser.header)
        text = resp.body.decode()
        return Selector(text=text)

    @staticmethod
    def parse_pdflibr(response, server_name, ph_num_fetched_time):
        table = response.xpath('(//table[@class="table table-hover"])[last()]')
        table_headers = [xpath_text_no_spaces(th) for th in table.xpath('.//th')]
        result_list = []
        for tr in table.xpath('tbody//tr'):
            values = [xpath_extract_all_text_strip(td) for td in tr.xpath('.//td')]
            a_dict = dict(zip(table_headers[1:], values[1:]))
            msg_received_time = a_dict['发送日期']
            if maya.when(msg_received_time, timezone=LOCAL_TIMEZONE) > ph_num_fetched_time:
                result_list.append(a_dict)
                if server_name and server_name in a_dict['短信内容']:
                    return True, [a_dict]
            else:
                break
        # 如果无法判断对方想要获取的短信信息中包含哪些内容,
        # 则发送该手机号码获取到的最新的5条短信
        return False, result_list[:5]

    @staticmethod
    def parse_yunduanxin(response, server_name, ph_num_fetched_time):
        item_xpath = '//div[contains(@class, "row border-bottom table-hover")]'
        headers = ['电话号码', '发送日期', '短信内容']
        result_list = []
        for div in response.xpath(item_xpath):
            values = [xpath_extract_all_text_strip(_div) for _div in div.xpath('./div')]
            from_where = values[0]
            values[0] = from_where[:from_where.find('From')].strip()
            a_dict = dict(zip(headers, values))
            msg_received_time = a_dict['发送日期']
            if maya.when(msg_received_time, timezone=LOCAL_TIMEZONE) > ph_num_fetched_time:
                result_list.append(a_dict)
                if server_name and server_name in a_dict['短信内容']:
                    return True, [a_dict]
            else:
                break
        return False, result_list[:5]


@route(r'/register_server/?')
class MobilePhoneNumberCaptchaHandler(RequestHandler):
    def initialize(self):
        self._register_cmd_match = re.compile(r'(?:注册)?(.*)')
        self.db_mgr = DatabaseManager(g_db)

    @gen.coroutine
    def handle_request(self, server_name):
        query = self.db_mgr.get_data_by_name('ph_num')
        data_list = list(query.fetchall())
        data = list(choice(data_list))
        if server_name:
            msg = f'手机号码为: {data[0]} (注册{server_name}), 短信验证码稍微发送给您!'
        else:
            msg = f'手机号码为: {data[0]}, 短信验证码稍微发送给您!'
        yield MessageSender.send_msg_2_weixin({'text': msg})
        data_dict = dict(zip(['ph_num', 'url'], data[:2]))
        data_dict['server_name'] = server_name
        data_dict['ph_num_fetched_time'] = maya.now()
        task = CaptchaTask(**data_dict)
        TASK_QUEUE.append(task)
        self.write(msg)

    @gen.coroutine
    def get(self, *args, **kwargs):
        server_name = self.get_argument('name', '')
        yield self.handle_request(server_name)

    @gen.coroutine
    def post(self, *args, **kwargs):
        post_data = self.request.body.decode('utf-8')
        post_json = []
        try:
            post_json = json.loads(post_data)
        except Exception:
            if '\r\n\r\n' in post_data:
                post_data = re.search(r'\r\n\r\n(.+?)\r\n', post_data).group(1)
                post_json = json.loads(post_data)
        if post_json:
            server_name = post_json[1][0]
            yield self.handle_request(server_name)
        else:
            self.set_status(400, 'wrong post data')


def make_app():
    _app = Application(ROUTE_LIST)
    return _app


class MessageSender:
    @staticmethod
    def gen_detail_msg(msg_list: list, no_server_name=False):
        msg = '\n'.join([WEIXIN_MSG_TEMPLATE.format(**msg_dict) for msg_dict in msg_list])
        if no_server_name:
            msg = '由于无法判断您在注册什么服务,所以发送了下列的短信供你筛选:\n' + msg
        return msg

    @staticmethod
    @gen.coroutine
    def send_msg_2_weixin(msg_dict):
        try:
            print(msg_dict)
            url = SC_FTPP_URL + '?' + urlencode(msg_dict)
            yield Parser.http_client.fetch(url, headers=Parser.header)
            CALL_SERVER_TIMES_QUEUE.append(int(time.time()))
        except Exception:
            traceback.print_exc()

    @gen.coroutine
    def gen_a_request_task(self, task: CaptchaTask, max_retry_times=5):
        timedelta = maya.now().epoch - task.ph_num_fetched_time.epoch
        if timedelta < 15:
            yield gen.sleep(30)
        if not task.server_name:
            yield gen.sleep(30)
        result = []
        while max_retry_times - task.request_times:
            try:
                host_name = urlparse(task.url).hostname
                task.request_times += 1
                print(f'{task.ph_num} 第{task.request_times}次获取验证码中.... {task.url}')
                response = yield Parser.get_response(task.url)
                parse_method = getattr(Parser, PARSER_METHOD_MAPPING[host_name], None)
                if parse_method is None:
                    print(f'{task.ph_num} wrong phone number get!')
                    return
                status, result = parse_method(response, task.server_name, task.ph_num_fetched_time)
                if not task.server_name:
                    break
                if not status:
                    yield gen.sleep(10)
                else:
                    break
            except Exception:
                print(f'something wrong when get captcha about {task}')
                traceback.print_exc()
                yield gen.sleep(2)
        if task.request_times == max_retry_times:
            print(f'max retry times to get {task.ph_num}\'s captcha! {task.server_name}')
        if result:
            msg_dict = {
                'text': f'{task.ph_num} 获取到的验证码信息',
                'desp': self.gen_detail_msg(result) if status else self.gen_detail_msg(result, True)
            }
            yield self.send_msg_2_weixin(msg_dict)
        else:
            print(f'there is no new message about {task.ph_num}')

    @gen.coroutine
    def send_msg(self):
        while 1:
            if not TASK_QUEUE:
                print('任务队列为空,等待下一次轮训...')
                yield gen.sleep(2)
                continue
            now = maya.now().epoch
            while CALL_SERVER_TIMES_QUEUE:
                if now - CALL_SERVER_TIMES_QUEUE[0] > 24 * 60 * 60:
                    CALL_SERVER_TIMES_QUEUE.popleft()
                else:
                    break
            if len(CALL_SERVER_TIMES_QUEUE) >= 500:
                print('Server酱 每天限制调用500次, 目前已经调用超过500次,稍后提供服务,谢谢')
                yield gen.sleep(10)
                continue

            task_list = []
            for i in range(len(TASK_QUEUE)):
                a_task = TASK_QUEUE.popleft()
                task_list.append(self.gen_a_request_task(a_task))
                if len(task_list) == 5:
                    break
            yield []


@gen.coroutine
def check_ph_num_is_valid():
    while 1:
        try:
            query = g_db.get_ph_num()
            data_list = list(query.fetchall())
            for data in data_list:
                if int(time.time()) - data[-1] > 2 * 60 * 60:
                    g_db.del_data(data)
                    print(f'mobile_phone_number[{data[0]}] has not updated for more than 2 hours')
            yield gen.sleep(10)
        except Exception:
            traceback.print_exc()
            yield gen.sleep(10)


def run():
    global g_db
    tornado.options.define("port", default=8888, help="run on the given port", type=int)
    tornado.options.define("db_file_path", default=None)
    tornado.options.parse_command_line()
    g_db = SqliteDB(tornado.options.options.db_file_path)
    app = make_app()
    msg_sender = MessageSender()
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(tornado.options.options.port)
    io_loop = tornado.ioloop.IOLoop.current()
    io_loop.add_callback(msg_sender.send_msg)
    io_loop.add_callback(check_ph_num_is_valid)
    io_loop.start()
    g_db.close()


if __name__ == '__main__':
    run()
