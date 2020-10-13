# coding: utf8
import re
import os
import time
import codecs
import argparse
from data_config import svn_config
from svn_model import SVNManager
from redis_model import RedisManager


# 读取当前的版本号
def read_revison_file(file):

    with codecs.open(file, 'r', 'utf-8') as f:
        return int(f.read().strip())


# 更新下一个版本号
def update_revision_file(file, revision):
    print('[Test]更新记录的版本号信息，版本号为: '+str(revision))
    with codecs.open(file, 'w', 'utf8') as f:
        f.write(str(revision))

# 解析单条log信息
def argse_log_info(log_message):
    info = {}
    if log_message and log_message[1]:
        single_number = ''
        pattern = re.compile('JX3M-\d+')
        single_number_message = pattern.match(log_message[1])
        if single_number_message:
            single_number = single_number_message.group(0)

        if single_number and single_number not in info:
            info[single_number] = {}
            if log_message.changelist:
                for item in log.changelist:
                    # 保持只有一个文件 不重复
                    if item[1] not in info[single_number] and not item[1].endswith('.meta'):
                        info[single_number][item[1]] = {'revision': log_message.revision}

    return info


if __name__ == '__main__':

    # redis_manager = RedisManager()
    # redis_manager.clear_all_value()
    # file_list = redis_manager.get_value('JX3M-104415')
    # for file in file_list:
    #     print('[Test]获取到的文件为: '+str(file))

    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--revision-path', help="revision_path", required=True)
    args = parser.parse_args()
    revision_file = args.revision_path
    if not os.path.exists(revision_file):
        print('[Test]当前未出去传入revision文件,请传入')
        os.exit(1)

    redis_manager = RedisManager()
    svn_manager = SVNManager(svn_config['url'])

    from_revision = 0

    to_revision = read_revison_file(revision_file)
    max_revision = svn_manager.get_new_revision()
    print('[Test]第一次获取当前项目最大版本号为: ' + str(max_revision))

    while True:
        if to_revision == max_revision:
            print('[Test]当前从文件读到的版本已经为项目最新版本所有不需要再查看log信息')
            time.sleep(5 * 60)
        else:
            begin_time = time.time()
            if to_revision == 0:
                from_revision = to_revision
                to_revision = to_revision + 10000
                print('[Test]首次遍历: 当前从版本: ' + str(from_revision) + ' 至尾版本: ' + str(to_revision))
            else:
                from_revision = to_revision
                to_revision = to_revision + 10000
                print('[Test]后续遍历: 当前从版本: ' + str(from_revision) + ' 至尾版本: ' + str(to_revision))

            if to_revision > max_revision:
                to_revision = max_revision
                print('[Test]遍历超出上限: 赋值给最新版本即可,当前从版本: ' + str(from_revision) + ' 至尾版本: ' + str(to_revision))

            # 获取from_revision ~ to_revision 的log信息
            svn_log = svn_manager.get_log(from_revision, to_revision)
            count = 0
            current_revision = 0
            for log in svn_log:
                # print('读取到的log信息为: '+str(log))
                info = argse_log_info(log)
                if info:
                    for issued, path_info in info.items():
                        for path, revision_info in path_info.items():
                            redis_manager.set_value(issued, path)
                            count = count + 1
                            print('[Test]当前项redis插入的单号为: '+issued+' 文件个数为: '+str(count))
                            if current_revision < revision_info['revision']:
                                current_revision = revision_info['revision']
            if current_revision == 0:
                current_revision = to_revision

            update_revision_file(revision_file, current_revision)
            print('[Test]遍历10000个版本需要花费时间为: '+str(begin_time - time.time()))

        to_revision = read_revison_file(revision_file)
        max_revision = svn_manager.get_new_revision()




