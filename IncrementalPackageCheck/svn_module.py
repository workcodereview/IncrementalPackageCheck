# coding: utf8

import re
import svn.remote

SVN_URL = 'svn://xsjreposvr3.rdev.kingsoft.net/JX3M'
SVN_USERNAME = 'scm_builder_jx3m'
SVN_PASSWORD = '_ZMvNHvP0C'
SVN_CLIENT = svn.remote.RemoteClient(SVN_URL, username=SVN_USERNAME, password=SVN_PASSWORD)


class SVN:
    def __init__(self, revision_from, revision_to=None):
        self.revision_from = revision_from
        self.revision_to = revision_to
        # self.issue_commit = self.__load_issue_commit()
        self.__reload()

    def __reload(self):
        self.issue_commit = {}
        self.__load_commit()
        # self.__load_diff()

    # 获取提交日志
    def __load_commit(self):
        for log in SVN_CLIENT.log_default(revision_from=self.revision_from, revision_to=self.revision_to, changelist=True):
            # print('SVN commit %s' % log.revision)
            self.__save_issue_commit(log)
        # 保存结束版本号
        if self.issue_commit and self.revision_to is None:
            self.revision_to = log.revision

    def __load_diff(self):
        # print 'SVN diff %d %d' % (self.revision_from, self.revision_to)
        for log in SVN_CLIENT.diff(self.revision_from, self.revision_to):
            log

    # 保存问题变更资源
    def __save_issue_commit(self, log):
        # 提交单号
        issue_id = None
        issue_id_search = re.search('^JX3M-\d+', log.msg)
        if issue_id_search:
            issue_id = issue_id_search.group()
        if issue_id not in self.issue_commit:
            self.issue_commit[issue_id] = {}

        # 提交列表
        for change in log.changelist:
            change_type, change_path = change
            self.issue_commit[issue_id][change_path] = {'type': change_type, 'path': change_path}

    # 获取文件大小
    def get_file_size(self, path):
        size = 0
        try:
            for info in SVN_CLIENT.list(extended=True, rel_path=path):
                size = info['size']
        except Exception:
            # svn已删除文件无法取得文件大小
            pass
        return size
