# coding: utf8
# 基于最初版本统计每个单所对应的多个文件

import svn.remote
from data_config import svn_config

class SVNManager:
    def __init__(self, url):
        self._rclient = svn.remote.RemoteClient(url, username=svn_config['username'], password=svn_config['password'])

    # 返回log信息
    def get_log(self, from_revision, to_revision=None):
        message = ''
        if to_revision:
            message = self._rclient.log_default(revision_from=from_revision, revision_to=to_revision, changelist=True)
        else:
            message = self._rclient.log_default(revision_from=from_revision, changelist=True)
        print('[SVN]获取从版本'+str(from_revision)+'开始,到版本'+str(to_revision)+'结束log信息完成')
        return message

    def get_new_revision(self):
        info = self._rclient.info()
        return int(info['commit_revision'])


