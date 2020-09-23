# coding: utf8
import  re
import  sys
import  json
import requests
from data_config import analy_platform

# 获取版本对应的aba_bundle信息
class Analy_Plat:
    def __init__(self):
        self._package_type = 'Android'
        self._package_url = analy_platform['package_url']
        self._aba_bundle_url = analy_platform['ababundle_url']
        self.__reload()

    def __reload(self):
        self._aba_bundle_id = self.get_aba_id() # 获取可以得到aba_bundle内容的id

# 获取aba_bundle所在路径
    def get_aba_id(self):
        _aba_bundle_id = {}
        r = requests.get(self._package_url, json={'query':{'disable': False, 'info.platform': self._package_type, 'status': True}})
        data_content = r.json()
        count = 0
        if data_content['data']:
            for index, content in enumerate(data_content['data']):
                count = count + 1
                if count > 10:
                    break
                if content['id'] not in _aba_bundle_id:
                    key = content['id']
                    aba_bundle_url = self._aba_bundle_url + '/%s/original/aba_bundle.json' % key

                    if 'breadcrumb' in content['info'] and 'svn' in content['info'] :
                        divide = ''
                        if 'txpublish' in content['info']['breadcrumb']:
                            divide = 'txpublish'
                        elif 'trunk' in content['info']['breadcrumb']:
                            divide = 'trunk'
                        if key not in _aba_bundle_id:
                            _aba_bundle_id[key] = {'rootmessage': divide, 'platform': content['info']['platform'],'aba_bundle_url': aba_bundle_url,
                                                'timestamp': content['info']['timestamp'], 'svn': content['info']['svn']}
        return  _aba_bundle_id

# 获取aba_bundle内容信息 并且组合成可简单查询的字典
    def get_aba_bundle_dict(self):
        trunk_android_bundle = {}
        txpublish_android_bundle = {}
        for key, value in self._aba_bundle_id.items():
            dict_key = value['svn'] + '-' + value['timestamp']
            req = requests.get(value['aba_bundle_url'])
            if req.status_code != 200:
                print(u'aba_bundle.json 获取失败\nstatus_code=%d\n%s' % (req.status_code, aba_bundle_url))
                continue
            aba_content = req.content.decode().split('\n')

            bundle_info = {}
            for line_str in aba_content:
                line_str = line_str.strip()
                if line_str == '':
                    break
                line_json = json.loads(line_str)
                bundle_name = re.search('[^\\\\]+$', line_json['bundle']).group()
                bundle_size = line_json['bundleSize']
                bundle_info[bundle_name] = {
                    'name': bundle_name,
                    'size': bundle_size,
                    'platform': value['platform'],
                    'filelist': []
                }

                for file_info in line_json['fileList']:
                    asset_path = file_info['f']
                    if asset_path == 'ABO':
                        continue
                    bundle_info[bundle_name]['filelist'].append(asset_path.upper())
                # 按照主干分支 svn 分别存放bundle ---> file 信息
                if value['rootmessage'] == 'trunk':
                    if dict_key not in trunk_android_bundle:
                        trunk_android_bundle[dict_key] = {}
                        trunk_android_bundle[dict_key] = bundle_info
                    else:
                        trunk_android_bundle[dict_key] = bundle_info

                if value['rootmessage'] == 'txpublish':
                    if value['svn'] not in txpublish_android_bundle:
                        txpublish_android_bundle[dict_key] = {}
                        txpublish_android_bundle[dict_key] = bundle_info
                    else:
                        txpublish_android_bundle[dict_key] = bundle_info
        return trunk_android_bundle, txpublish_android_bundle
