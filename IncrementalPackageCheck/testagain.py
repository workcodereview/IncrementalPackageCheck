# coding: utf8
import time
from Jira_model import JX3M
from analy_platform_model import Analy_Plat
from data_config import jx3m_page_Platform

# 传入对应平台的bundle文件 file 文件 查找
def check_asset_bundle(svn_info, asset_path, root_type, platform):
    result_message = {}
    path = asset_path
    if '/trunk' in path:
        path = path.strip().replace('/trunk/JX3Pocket/', '')
    if '/branches-rel' in path:
        path = path.strip().replace('/branches-rel/tx_publish/JX3Pocket/', '')

    for svn, file_message in svn_info.items():
        if path in  file_message:
            result_message = {
                'root': root_type,  # trunk txpublish txhotfix
                'file': asset_path,  # /trunk/JX3Pocket/ /branches-rel/tx_publish /txhotfix
                'platform': platform,  # Android iOS
                'svn': svn,  # 查找版本包
                'package_size': file_message[path]['package_size'],  # 版本包的大小
                'bundle_name': file_message[path]['bundle_name'],  # 文件所在的bundle中
                'bundle_size': file_message[path]['bundle_size'],  # bundle的大小
                # 版本包的路径
                'revison_url': jx3m_page_Platform['revison_url'].format(platform, file_message[path]['package_timestamp']),
                # bundle包的路径
                'bundle_name_url': jx3m_page_Platform['bundle_url'].format(platform, file_message[path]['package_timestamp'],
                                                                           file_message[path]['bundle_name'])
            }
            break
    return result_message

# 分析查找每个单的信息 返回整个单所有文件的结果
def analy_single_number(trunk_bundle, txpublish_bundle, hotfix_bundle, root_message):
    return_result = {'issueid': '', 'version': '', 'total': [], 'data': {}}
    single_number_result = {}

    for root_type, file_list in root_message.items():
        for file in file_list:
            # print('[Test]当前分析的文件为: ',file)
            android_result = {}
            ios_result = {}

            if file not in single_number_result:
                single_number_result[file] = {}


            if root_type == 'trunk':
                android_result = check_asset_bundle(trunk_bundle['Android'], file, root_type, 'Android')
                ios_result = check_asset_bundle(trunk_bundle['iOS'], file, root_type, 'iOS')
            elif root_type == 'txpublish':
                android_result = check_asset_bundle(txpublish_bundle['Android'], file, root_type, 'Android')
                ios_result = check_asset_bundle(txpublish_bundle['iOS'], file, root_type, 'iOS')
                # if not android_result and not ios_result:
                #     android_result = check_asset_bundle(trunk_bundle['Android'], file, root_type, 'Android')
                #     ios_result = check_asset_bundle(trunk_bundle['iOS'], file, root_type, 'iOS')
            elif root_type == 'tx_publish_hotfix':
                android_result = check_asset_bundle(hotfix_bundle['Android'], file, root_type, 'Android')
                ios_result = check_asset_bundle(hotfix_bundle['iOS'], file, root_type, 'iOS')

            if android_result:
                # print('[Test]Android 有返回数据',str(android_result))
                single_number_result[file]['Android'] = android_result
            if ios_result:
                # print('[Test]iOS 有返回数据',str(ios_result))
                single_number_result[file]['iOS'] = ios_result

    return_result['data'] = single_number_result
    return return_result

# 指定root 平台 获取最新的包版本 在返回所有的版本包 便于展示
def find_max_revison(result, root_type, plat):
    max_svn = 0
    max_new_message = {}
    svn_list = {}

    for path, platform_info in result['data'].items():
        if root_type in path:
            for plat_form, bundle_info in platform_info.items():
                if plat_form == plat:
                    if max_svn < int(bundle_info['svn']):
                        max_svn = int(bundle_info['svn'])
                        max_new_message = bundle_info
                        if bundle_info['svn'] not in svn_list:
                            svn_list[bundle_info['svn']] = {}
                        svn_list[bundle_info['svn']] = {'revison_url': bundle_info['revison_url'], 'pakage_size': bundle_info['package_size'] }  # 保存所有小于最新的包版本
    if max_svn != 0:
        svn_list.pop(str(max_svn))

    return max_new_message, svn_list

# 计算大小
def calc_pakcage_size(size):
    package_size = size
    if 'MB' in package_size:
        package_size = package_size.replace('MB', '')
        package_size = float(package_size)*1024*1024
    elif 'KB' in package_size:
        package_size = float(package_size.replace('MB', ''))*1024
    return str(package_size)

# 组织返回结果格式
def Encapsulation_result(platform_message, svn_list_info, platform, root):
    # print('platform_message: ',str(platform_message))
    # print('svn_list_info:',str(svn_list_info))
    package_message = {}
    previdict_message = []

    if platform_message:
        package_message['path'] = platform_message['root']
        package_message['platform'] = platform
        if root == '/trunk':
            if 'install_info' not in package_message:
                package_message['install_info'] = {}
            package_message['install_info']['svn'] = platform_message['svn']
            package_message['install_info']['revison_url'] = platform_message['revison_url']
            package_message['install_info']['package_size'] = calc_pakcage_size(platform_message['package_size'])
        elif root == '/branches-rel/tx_publish' or root == '/branches-rel/tx_publish_hotfix':
            if 'update_info' not in package_message:
                package_message['update_info'] = {}
            package_message['update_info']['svn'] = platform_message['svn']
            package_message['update_info']['revison_url'] = platform_message['revison_url']
            package_message['update_info']['package_size'] = calc_pakcage_size(platform_message['package_size'])


    if svn_list_info:
        temp_dict = {}
        for svn, svn_info in svn_list_info:
            temp_dict['svn'] = svn
            temp_dict['revison_url'] = svn_info['revison_url']
            temp_dict['package_size'] = calc_pakcage_size(svn_info['package_size'])
            previdict_message.append(temp_dict)
            temp_dict.clear()

        if 'forcast_info' not in package_message:
            package_message['forcast_info'] = {}
            package_message['forcast_info'] = previdict_message

    return package_message

# 组织安装包 更新包格式
def comcat_result(result,root, plat):
    message, svn_info = find_max_revison(result_total, root, plat)
    temp_result = Encapsulation_result(message, svn_info, plat, root)
    if temp_result:
        result['total'].append(temp_result)
    return result

# 预测的涉及的包的信息展示
def concat_preview_pakcage(svn_info):
    message = ''
    if len(svn_info) < 0:
        print('[Test]当前提交单文件均处于同一版本包中,不存在预测包信息')
        return message

    for revison, url in svn_info.items():
       temp_message = '[版本包'+revison+'|'+url+']'
       if len(message + temp_message) < 32767:
           message += temp_message
    return message

def merge_content(result, root, platform):
    content = ''
    if not result:
        return content

    color_message = jx3m_page_Platform['color_green']  # 默认是绿色 全部包括
    new_message, svn_info = find_max_revison(result, root, platform)
    if new_message:
        preview_message = concat_preview_pakcage(svn_info)
        if preview_message != '':
            print('[Test]存在预测更新包信息,更换颜色,preview_message:',preview_message)
            color_message = jx3m_page_Platform['color_orige']

        package_size = new_message['package_size']
        if 'MB' in package_size:
            package_size = package_size.replace('MB', '')
        elif 'KB' in package_size:
            package_size = round(int(package_size.replace('MB', ''))/1024, 2)
        else:
            package_size = round(int(package_size)/1024, 2)

        if '/branches-rel' in root:
            root = root.replace('/branches-rel', '')

        root_platform = root + ' ' +platform
        if root == '/trunk':
            # print('[Test]主干信息合并展示')
            mesage_temp = color_message.format('版本包:') + '['+new_message['svn'] + '('+ str(package_size)+'MB)|' + new_message['revison_url'] + ']'
            content = '|'+root_platform+'|'+mesage_temp+'|' + ' |' + preview_message + ' |\n'
        else:
            # print('[Test]分支或者热更信息合并展示')
            mesage_temp = color_message.format('版本包:') + '[' + new_message['svn'] + '(' + str(package_size) + 'MB)|' + new_message['revison_url'] + ']'
            content = '|' + root_platform + ' | |'+ mesage_temp + '|' + preview_message + ' |\n'
    return content

def check_out_index(first_content, second_content):
    if len(first_content + second_content) > 32767:
        return second_content
    else:
        return first_content + second_content

if __name__ == '__main__':

    # 取aba_bundle信息
    analy = Analy_Plat()
    print('[Test]bundle信息获取完成')
    # 主干获取bundle测试通过
    trunk_path_to_bundle, txpublish_path_to_bundle, hotfix_path_to_bundle = analy.get_aba_bundle_dict()
    jx3m = JX3M()
    single_number_assets = jx3m.get_single_number_assets()
    print('[Test]单号长度: ',len(single_number_assets))

    count = 1
    begin_time = time.time()
    # print('txpublish_path_to_bundle: ',str(txpublish_path_to_bundle))
    for single_number, root_info in single_number_assets.items():
        print('[Test]当前正在分析第' + str(count) + '个提交单,单号为:' + single_number)
        # 获取当前单的所有信息 文件对应bundle 或者 没有找到bundle的文件列表
        result_total = analy_single_number(trunk_path_to_bundle, txpublish_path_to_bundle, hotfix_path_to_bundle, root_info)
        if count == 11:
            break
        count = count + 1
        # 向结果添加单号和版本信息 Android iOS 安装包信息 预测包信息
        result_total['issueid'] = single_number
        result_total['version'] = jx3m.version_info['version']
        result_total = comcat_result(result_total, '/trunk', 'Android')
        result_total = comcat_result(result_total, '/trunk', 'iOS')
        result_total = comcat_result(result_total, '/branches-rel/tx_publish', 'Android')
        result_total = comcat_result(result_total, '/branches-rel/tx_publish', 'iOS')
        result_total = comcat_result(result_total, '/branches-rel/tx_publish_hotfix', 'Android')
        result_total = comcat_result(result_total, '/branches-rel/tx_publish_hotfix', 'iOS')

        jx3m.commit_single_number_assetinfo(single_number, result_total)
        # print('result_total: ', str(result_total))

    print('提交单数量：', str(count))
    print('[Test]analy single number end: ', str(begin_time - time.time()))


