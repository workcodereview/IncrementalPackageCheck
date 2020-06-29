# coding: utf8

import re
import sys
import json
import codecs
import logging
import requests
import xml.etree.ElementTree as ET

QB_URL = 'http://j3m.rdev.kingsoft.net:8810'
QB_USERNAME = 'foranalyse'
QB_PASSWORD = 'anRes0756'
QB_REQUESTS = requests.Session()
QB_REQUESTS.auth = (QB_USERNAME, QB_PASSWORD)

RESOURCE_URL = 'http://10.11.10.86/download/resource_package'


class QB:
    def __init__(self, build_id, aba_bundle_path=None):
        self.build_id = build_id
        self.aba_bundle_path = aba_bundle_path
        self.__reload()

    def __reload(self):
        self.build_svn, self.build_time = self.__load_build_info()
        self.asset_cache_data = self.__load_asset_cache_data()
        self.bundle_info, self.asset_path_to_bundle = self.__load_aba_bundle()

    # 获取svn版本
    def __load_build_info(self):
        build_svn, build_time = None, None
        url = QB_URL + '/rest/builds/%d' % self.build_id
        req = QB_REQUESTS.get(url)
        if req.status_code != 200:
            logging.error(u'builds获取失败\nstatus_code=%d\n%s' % (req.status_code, url))
            sys.exit(1)
        root = ET.fromstring(req.content)
        for item in root.iterfind('secretAwareVariableValues/entry'):
            if 'var_svn_version' == item.findtext('string'):
                build_svn = int(item.findtext('com.pmease.quickbuild.SecretAwareString/string'))
            if 'var_BuildInfo_UnixTimestampMillis' == item.findtext('string'):
                build_time = int(item.findtext('com.pmease.quickbuild.SecretAwareString/string'))
        return build_svn, build_time


    # 预处理生成
    def __load_asset_cache_data(self):
        result = {}
        url = QB_URL + '/download/%d/artifacts/AssetCacheData.txt' % self.build_id
        req = QB_REQUESTS.get(url)
        if req.status_code != 200:
            logging.error(u'AssetCacheData.txt 获取失败\nstatus_code=%d\n%s' % (req.status_code, url))
            sys.exit(1)
        data = json.loads(req.content)
        for id in data.keys():
            if data[id]['productFileList'] is None:
                continue
            asset_path = data[id]['assetPath'].upper()
            if asset_path not in result:
                result[asset_path] = []
            result[asset_path] += data[id]['productFileList']
        return result

    # 资源hash
    def __load_asset_hash(self):
        result = {}
        url = QB_URL + '/download/%d/artifacts/Jx3GameAssetHash.txt' % self.build_id
        req = QB_REQUESTS.get(url)
        if req.status_code != 200:
            logging.error(u'AssetCacheData.txt 获取失败\nstatus_code=%d\n%s' % (req.status_code, url))
            sys.exit(1)
        data = json.loads(req.content)
        for id in data.keys():
            if data[id]['productFileList'] is None:
                continue
            asset_path = data[id]['assetPath'].upper()
            if asset_path not in result:
                result[asset_path] = []
            result[asset_path] += data[id]['productFileList']
        return result

    # bundle资源
    def __load_aba_bundle(self):
        bundle_info = {}
        asset_path_to_bundle = {}
        if self.aba_bundle_path:
            print('use inoput aba_bundle file')
            with codecs.open(self.aba_bundle_path, 'r', 'utf-8') as a_file:
                aba_content = a_file.read().strip().splitlines()
        else:
            print('use build id for aba_bundle.json')
            url = RESOURCE_URL + '/%d/original/aba_bundle.json' % self.build_time
            req = requests.get(url)
            if req.status_code != 200:
                logging.error(u'aba_bundle.json 获取失败\nstatus_code=%d\n%s' % (req.status_code, url))
                sys.exit(1)
            aba_content = req.content.decode().split('\n')

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
                'files': [],
            }
            for file_info in line_json['fileList']:
                asset_path = file_info['f']
                if asset_path == 'ABO':
                    continue
                bundle_info[bundle_name]['files'].append(asset_path)
                # 资源路径对应bundle信息
                asset_path_upper = asset_path.upper()
                if asset_path_upper not in asset_path_to_bundle:
                    asset_path_to_bundle[asset_path_upper] = {}
                asset_path_to_bundle[asset_path_upper].clear()
                asset_path_to_bundle[asset_path_upper][bundle_name] = bundle_size
        return bundle_info, asset_path_to_bundle

    # 资源路径查所在bundle
    def asset2bundle(self, path):
        path_upper = path.upper()
        if path_upper not in self.asset_path_to_bundle:
            return {}
        return self.asset_path_to_bundle[path_upper]
