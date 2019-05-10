downloader_middleware
-------------------
1. 为每个request增加默认的error_back,如果它没有error_back 的话,这样就可以减少代码量
2. 关键字过滤(从response过滤):
    * 从 response.text 过滤关键词
    * 从 response.url 过滤关键词
    * 从 response.header 过滤关键词
3. 增加cookie 池的功能, 使得request能够添加额外的cookie(比如登录之后获取的cookie)
4. 检查response body 在 http status code 为200的时候是否为空
5. 随机增加user-agent
6. 切换代理

pipelines
-------------------
1. 根据item的 _id 字段或者 _dup_str 字段去重
2. 根据settings中定义的 FIELDS_JSON_SCHEMA,检查是否包含需要的字段

spider_middleware
-------------------
1. 将一个response生成的parsed_item组装为列表,以便pipeline批量写入到目标数据库,提高效率

utils
-------------------
1. dianping_css_crack.py: 破解大众点评加密数字和文字
