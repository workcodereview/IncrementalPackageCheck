# coding: utf8

import sys
import logging
import requests

JIRA_URL = 'http://jx3m.rdev.kingsoft.net:8881'
JIRA_USERNAME = 'svnchecker'
JIRA_PASSWORD = 'mimashi1101'
JIRA_REQUESTS = requests.Session()
JIRA_REQUESTS.auth = (JIRA_USERNAME, JIRA_PASSWORD)


class JIRA:
    def __init__(self, issue_id=None):
        self.issue_id = issue_id
        self.__reload()

    def __reload(self):
        self.issue_info = {}
        if self.issue_id is None:
            return
        self.issue_info = self.__load_issue_info()

    def __get_obj_value(self, obj, keys):
        if len(keys) == 0:
            return obj
        if keys[0] not in obj:
            return None
        return self.__get_obj_value(obj[keys[0]], keys[1:])

    # 加载问题信息
    def __load_issue_info(self):
        print 'JIRA load %s' % self.issue_id
        url = JIRA_URL + '/rest/api/2/issue/' + self.issue_id
        req = JIRA_REQUESTS.get(url)
        if req.status_code != 200:
            logging.error(u'jira获取问题信息失败\nstatus_code=%d\n%s' % (req.status_code, url))
            sys.exit(1)
        return req.json()

    # 设置问题号
    def set_issue_id(self, issue_id):
        self.issue_id = issue_id
        self.__reload()

    # 获取问题标题
    def get_issue_title(self):
        return self.__get_obj_value(self.issue_info, ['fields', 'summary'])

    # 获取问题类型
    def get_issue_type(self):
        return self.__get_obj_value(self.issue_info, ['fields', 'issuetype', 'name'])

    # 获取问题父号
    def get_issue_parent_id(self):
        return self.__get_obj_value(self.issue_info, ['fields', 'parent', 'key'])

    # 获取问题父标题
    def get_issue_parent_title(self):
        return self.__get_obj_value(self.issue_info, ['fields', 'parent', 'fields', 'summary'])

    # 获取问题父类型
    def get_issue_parent_type(self):
        return self.__get_obj_value(self.issue_info, ['fields', 'parent', 'fields', 'issuetype', 'name'])
