# coding: utf8

# 向平台推送更新包信息  this model success
import re
import time
import requests
import datetime
from data_config import jx3m_page_Platform

class JX3M:
    def __init__(self):
        self._jx3m_url = jx3m_page_Platform['jx3m_page_url']
        self._upload_url = jx3m_page_Platform['upload_url']
        self._single_number_url = jx3m_page_Platform['total_single_number_url']  # 记录提交单所有信息的地方
        self._URL_SEARCH = jx3m_page_Platform['URL_SEARCH']
        self._username = jx3m_page_Platform['username']
        self._password = jx3m_page_Platform['password']
        self.__reload()
        # print('[Jira]获取到的参数路径为:', self._jx3m_url, self._upload_url, self._URL_SEARCH)

    def __reload(self):
        self._version_info = self.get_latest_version()
        self._single_number_list = self.get_single_number_list()


    def get_latest_version(self):
        now_date = datetime.datetime.today()
        version_message = {'version': '', 'released': False, 'userReleaseDate': ''}
        r = requests.get(self._single_number_url, auth=(self._username, self._password))
        data = r.json()
        temp_diff = 40000
        for value in data:
            if 'released' in value and 'userReleaseDate' in value:
                if not value['released']:
                    current_find_time = datetime.datetime.strptime(value['userReleaseDate'], '%Y-%m-%d')
                    diffenrence = current_find_time - now_date
                    if abs(diffenrence.days) < temp_diff:
                        temp_diff = abs(diffenrence.days)
                        version_message = {'version': value['name'], 'released': False, 'userReleaseDate': value['userReleaseDate']}
        return version_message

    # 获取指定版本的提交单号
    def get_single_number_list(self):
        single_number_list = []
        if self._version_info['version']:
            print('[Jira]获取到最新要发的版本号: ',self._version_info['version'])
            r = requests.get(self._URL_SEARCH, params={'jql': 'type = 提交单 and fixVersion = ' + self._version_info['version'], 'maxResults': 1000},
                         auth=(self._username, self._password))
            data = r.json()
            if data and data['issues']:
                for index, value in enumerate(data['issues']):
                    single_number_list.append(value['key'])
            return single_number_list

    # 通过单获取日志 截取资源路径
    def get_log(self, single_number):
        # print('[Jira]get_log单号url为: ',self._jx3m_url.format(single_number))
        r = requests.get(self._jx3m_url.format(single_number), auth=(self._username, self._password))
        return r.json()

    def delete_log(self,single_number, item_id):
        print('[Jira]delete_log删除旧的备注信息')
        r = requests.delete(self._jx3m_url.format(single_number) + '/' + item_id, auth=(self._username, self._password))
        if r.status_code != 204:
            self.delete_log(single_number, item_id)

    # 此单无备注 第一次向单添加备注
    def commit_content(self,single_number,content):
        # data = {'body':content}
        r = requests.post(self._jx3m_url.format(single_number),
                          auth=(self._username, self._password), json={
                'body': content
            })
        r.json()

    # 此单已存在备注 更新备注
    def update_comment(self, single_number, comment):
        # 获取当前信息本单的log信息
        content_id = {}

        single_number_message = self.get_log(single_number)
        for value in single_number_message['comments']:
            if '更新包大小预测结果' in value['body']:
                content_id[value['id']] = value['body']

        if len(content_id) == 1:
            for item_id, body in content_id.items():
                if body != comment:
                    print('[Jira]有新的更新消息,需要删除当前更新包信息')
                    self.delete_log(single_number, item_id)
                    self.commit_content(single_number, comment)
                else:
                    print('[Jira]不需要更新当前更新包信息')
        elif len(content_id) > 1:
            for item_id, body in content_id.items():
                self.delete_log(single_number, item_id)
            self.commit_content(single_number, comment)
        else:
            print('[Jira]第一次提交更新包预测信息')
            self.commit_content(single_number, comment)

    # 获取过去十小时变动单号所包含的资源文件路径 包含主干和分支
    def get_single_number_assets(self):
        asset_path_dict = {}
        count = 1
        for single_number in self._single_number_list:
            count = count + 1

            if single_number not in asset_path_dict:
                asset_path_dict[single_number] = {}
            if 'trunk' not in asset_path_dict[single_number]:
                asset_path_dict[single_number]['trunk'] = []
            if 'txpublish' not in asset_path_dict[single_number]:
                asset_path_dict[single_number]['txpublish'] = []
            if 'tx_publish_hotfix' not in asset_path_dict[single_number]:
                asset_path_dict[single_number]['tx_publish_hotfix'] = []

            data = self.get_log(single_number)
            if data and data['comments']:
                for item in data['comments']:
                    asset_path_list = re.findall(r'{color:#[0-9a-z]+?}[!|+|\-](.*?){color}', item['body'])
                    if asset_path_list:
                        for value in asset_path_list:
                            if '/trunk' in value and 'Assets' in value and  not value.endswith('.meta'):
                                asset_path = value.strip()
                                if asset_path not in asset_path_dict[single_number]['trunk']:
                                    asset_path_dict[single_number]['trunk'].append(asset_path)

                            if '/branches-rel/tx_publish' in value and 'Assets' in value and not value.endswith('.meta'):
                                asset_path = value.strip()
                                if asset_path not in asset_path_dict[single_number]['txpublish']:
                                    asset_path_dict[single_number]['txpublish'].append(asset_path)

                            if '/branches-rel/tx_publish_hotfix' in value and 'Assets' in value and not value.endswith('.meta'):
                                asset_path = value.strip()
                                if asset_path not in asset_path_dict[single_number]['tx_publish_hotfix']:
                                    asset_path_dict[single_number]['tx_publish_hotfix'].append(asset_path)
        return asset_path_dict

    # 向平台提交单号信息
    def commit_single_number_assetinfo(self,single_number, content):
        print('[Jira]向平台上传当前提交单所有资源信息,当前提交单为:',single_number)
        print('[Jira]平台数据上传路径:',self._upload_url.format(single_number))
        r = requests.post(self._upload_url.format(single_number), json={'data': content})


