# coding: utf8
import  re
import  json
import requests
from data_config import analy_platform

# 获取版本对应的aba_bundle信息
class Analy_Plat:
    def __init__(self):
        # self._package_type = 'Android'
        self._package_url = analy_platform['package_url']
        self._aba_bundle_url = analy_platform['ababundle_url']
        # self.aba_bundle_id = []

    # 需要获取当前Android iOS 所有现有的包的信息 aba_bundle_id 取了15条数据
    def get_all_aba_id(self):
        _aba_bundle_id = []
        r = requests.get(self._package_url, json={'query':{'disable': False, 'status': True}, 'sort':{'_id': -1}})
        data_content = r.json()
        count = 0
        if data_content['data']:
            for content in data_content['data']:
                count = count + 1
                if count == 30:
                    break
                key = content['id']
                aba_bundle_url = self._aba_bundle_url + '/%s/original/aba_bundle.json' % key
                # status 为true 并且 breadcrumb 有值 那么一定可以取到bundle信息
                if content['status'] and 'breadcrumb' in content['info'] and 'svn' in content['info']:
                    divide = ''
                    if 'txpublish' in content['info']['breadcrumb']:
                        divide = 'txpublish'
                    elif 'trunk' in content['info']['breadcrumb']:
                        divide = 'trunk'
                    elif 'txhotfix' in content['info']['breadcrumb']:
                        divide = 'txhotfix'

                    aba_bundle_info  = {'root': divide, 'platform': content['info']['platform'],'aba_bundle_url': aba_bundle_url,
                            'timestamp': content['info']['timestamp'], 'svn': content['info']['svn'], 'pakcagesize': content['info']['packagesize']}
                    _aba_bundle_id.append(aba_bundle_info)

        return _aba_bundle_id

    # 获取对应的aba_bundle信息 需要区分主干 分支 android ios平台
    def get_aba_bundle_dict(self):
        # 获取可以得到aba_bundle内容的id
        # self.aba_bundle_id = self.get_all_aba_id()

        trunk_path_to_bundle = {}
        txpublish_path_to_bundle = {}
        txhotfix_path_to_bundle = {}

        for value in self.get_all_aba_id():
            if value['platform'] not in trunk_path_to_bundle:
                trunk_path_to_bundle[value['platform']] = {}
            if value['svn'] not in trunk_path_to_bundle[value['platform']]:
                trunk_path_to_bundle[value['platform']][value['svn']] = {}

            if value['platform'] not in txpublish_path_to_bundle:
                txpublish_path_to_bundle[value['platform']] = {}
            if value['svn'] not in txpublish_path_to_bundle[value['platform']]:
                txpublish_path_to_bundle[value['platform']][value['svn']] = {}

            if value['platform'] not in txhotfix_path_to_bundle:
                txhotfix_path_to_bundle[value['platform']] = {}
            if value['svn'] not in txhotfix_path_to_bundle[value['platform']]:
                txhotfix_path_to_bundle[value['platform']][value['svn']] = {}

            req = requests.get(value['aba_bundle_url'])
            if req.status_code != 200:
                print(u'aba_bundle.json 获取失败\nstatus_code=%d\n%s' % (req.status_code, aba_bundle_url))
                continue
            aba_content = req.content.decode().split('\n')
            for line_str in aba_content:
                line_str = line_str.strip()
                if line_str == '':
                    break
                line_json = json.loads(line_str)
                bundle_name = re.search('[^\\\\]+$', line_json['bundle']).group()
                bundle_size = line_json['bundleSize']
                bundle_info = {
                    'bundle_name': bundle_name,
                    'bundle_size': bundle_size,
                    'package_size': value['pakcagesize'],
                    'package_timestamp':value['timestamp']
                }
                for file_info in line_json['fileList']:
                    asset_path = file_info['f']
                    if asset_path == 'ABO':
                        continue

                    # 存储主干信息 又有细分为Android iOS
                    if value['root'] == 'trunk':
                        if asset_path not in trunk_path_to_bundle[value['platform']][value['svn']]:
                            trunk_path_to_bundle[value['platform']][value['svn']][asset_path] = {}
                        trunk_path_to_bundle[value['platform']][value['svn']][asset_path] = bundle_info

                    # 存储分支信息 又有细分为Android iOS
                    if value['root'] == 'txpublish':
                        if asset_path not in txpublish_path_to_bundle[value['platform']][value['svn']]:
                            txpublish_path_to_bundle[value['platform']][value['svn']][asset_path] = {}
                        txpublish_path_to_bundle[value['platform']][value['svn']][asset_path] = bundle_info

                    # 存储hotfix信息 又有细分为Android iOS
                    if value['root'] == 'txhotfix':
                        if asset_path not in txhotfix_path_to_bundle[value['platform']][value['svn']]:
                            txhotfix_path_to_bundle[value['platform']][value['svn']][asset_path] = {}
                        txhotfix_path_to_bundle[value['platform']][value['svn']][asset_path] = bundle_info
        print('[Analy]bundle信息获取完成')
        return trunk_path_to_bundle, txpublish_path_to_bundle, txhotfix_path_to_bundle

    def get_aba_bundle_dict1(self):
        trunk_path_to_bundle = {}
        txpublish_path_to_bundle = {}
        txhotfix_path_to_bundle = {}

        if 'Android' not in trunk_path_to_bundle:
            trunk_path_to_bundle['Android'] = {}
        if 'iOS' not in trunk_path_to_bundle:
            trunk_path_to_bundle['iOS'] = {}

        if 'Android' not in txpublish_path_to_bundle:
            txpublish_path_to_bundle['Android'] = {}
        if 'iOS' not in txpublish_path_to_bundle:
            txpublish_path_to_bundle['iOS'] = {}

        if 'Android' not in txhotfix_path_to_bundle:
            txhotfix_path_to_bundle['Android'] = {}
        if 'iOS' not in txhotfix_path_to_bundle:
            txhotfix_path_to_bundle['iOS'] = {}

        for value in self.get_all_aba_id():
            req = requests.get(value['aba_bundle_url'])
            if req.status_code != 200:
                print(u'aba_bundle.json 获取失败\nstatus_code=%d\n%s' % (req.status_code, aba_bundle_url))
                continue
            try:
                aba_content = req.content.decode().split('\n')
                for line_str in aba_content:
                    line_str = line_str.strip()
                    if line_str == '':
                        break
                    line_json = json.loads(line_str)
                    bundle_name = re.search('[^\\\\]+$', line_json['bundle']).group()
                    bundle_size = line_json['bundleSize']
                    bundle_info = {
                        'bundle_name': bundle_name,
                        'bundle_size': bundle_size,
                        'package_size': value['pakcagesize'],
                        'package_timestamp': value['timestamp']
                    }
                    for file_info in line_json['fileList']:
                        asset_path = file_info['f']
                        if asset_path == 'ABO':
                            continue
                        if value['root'] == 'trunk':
                            if value['svn'] not in trunk_path_to_bundle[value['platform']]:
                                trunk_path_to_bundle[value['platform']][value['svn']] = {}

                            if asset_path not in trunk_path_to_bundle[value['platform']][value['svn']]:
                                trunk_path_to_bundle[value['platform']][value['svn']][asset_path] = {}
                            trunk_path_to_bundle[value['platform']][value['svn']][asset_path] = bundle_info
                        elif value['root'] == 'txpublish':
                            if value['svn'] not in txpublish_path_to_bundle[value['platform']]:
                                txpublish_path_to_bundle[value['platform']][value['svn']] = {}

                            if asset_path not in txpublish_path_to_bundle[value['platform']][value['svn']]:
                                txpublish_path_to_bundle[value['platform']][value['svn']][asset_path] = {}
                            txpublish_path_to_bundle[value['platform']][value['svn']][asset_path] = bundle_info
                        elif value['root'] == 'txhotfix':
                            if asset_path not in txhotfix_path_to_bundle[value['platform']][value['svn']]:
                                txhotfix_path_to_bundle[value['platform']][value['svn']][asset_path] = {}
                            txhotfix_path_to_bundle[value['platform']][value['svn']][asset_path] = bundle_info
            except Argument:
                print('[Analy]代码运行中错误Error: '+str(Argument))

        print('[Analy]bundle信息获取完成')
        return trunk_path_to_bundle, txpublish_path_to_bundle, txhotfix_path_to_bundle






