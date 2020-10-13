# coding: utf8
# 缓存单号对应文件列表

import redis
from data_config import redis_config

class RedisManager:
    def __init__(self):
        self._redis = redis.Redis(host=redis_config['host'],password=redis_config['password'], port=redis_config['port'],db=1, decode_responses=True)

    # 添加值 key --> list[file1, file2, file3,file4,]
    def set_value(self, key, value):
        self._redis.sadd(key, value)

    # 根据key值获取对应的文件list
    def get_value(self, key):
        # file_list = self._redis.get(key)
        file_list = self._redis.smembers(key)
        return file_list

    def clear_all_value(self):
        print('[Rdeis]清除数据库成功')
        self._redis.flushall(asynchronous=True)

    # 判断key是否在当前redis中
    def is_exist_key(self, key):
        if self._redis.exists(key):
            return True
        else:
            return False
