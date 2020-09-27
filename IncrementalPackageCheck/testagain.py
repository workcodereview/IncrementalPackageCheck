# coding: utf8

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
        for file_path, bundle_info in file_message.items():
            if file_path.upper() == path.upper():
                result_message = {
                    'root': root_type,  # trunk txpublish txhotfix
                    'file': asset_path,  # /trunk/JX3Pocket/ /branches-rel/tx_publish /txhotfix
                    'platform': platform,  # Android iOS
                    'svn': svn,  # 查找版本包
                    'package_size': bundle_info['package_size'] ,  # 版本包的大小
                    'bundle_name': bundle_info['bundle_name'],  # 文件所在的bundle中
                    'bundle_size': bundle_info['bundle_size'],  # bundle的大小
                    # 版本包的路径
                    'revison_url': jx3m_page_Platform['revison_url'].format(platform, bundle_info['package_timestamp']),
                    # bundle包的路径
                    'bundle_name_url': jx3m_page_Platform['bundle_url'].format(platform, bundle_info['package_timestamp'],
                                                                               bundle_info['bundle_name'])
                }
                break
    return result_message

# 提供在aba_bundle_dict中查找文件是否在bundle中 结果分为android ios
def check_asset_to_bundle_size(bundle_dict, asset_path, root_type):
    if not bundle_dict:
        print('[Test]bundle_dict is null')
        return
    # result_message = []
    android_result = check_asset_bundle(bundle_dict['Android'], asset_path, root_type, 'Android')
    ios_result = check_asset_bundle(bundle_dict['iOS'], asset_path, root_type, 'iOS' )
    return android_result,ios_result

# 分析查找每个单的信息 返回整个单所有文件的结果
def analy_single_number(trunk_bundle, txpublish_bundle, hotfix_bundle, root_message):
    return_result = []
    single_number_result = {}
    for root_type, file_list in root_message.items():
        for file in file_list:
            android_result = {}
            ios_result = {}

            if file not in single_number_result:
                single_number_result[file] = {}

            if root_type == 'trunk':
                android_result, ios_result = check_asset_to_bundle_size(trunk_bundle, file, root_type)
            elif root_type == 'txpublish':
                android_result, ios_result = check_asset_to_bundle_size(txpublish_bundle, file, root_type)
                if not android_result and not ios_result:
                    android_result, ios_result = check_asset_to_bundle_size(trunk_bundle, file, root_type)
            elif root_type == 'tx_publish_hotfix':
                android_result, ios_resultt = check_asset_to_bundle_size(hotfix_bundle, file, root_type)

            if android_result:
                single_number_result[file] = {'Android': android_result}
            if  ios_result:
                single_number_result[file] = {'iOS': ios_result}

            if single_number_result[file]:
                return_result.append(single_number_result)


    return return_result


# 指定root 平台 获取最新的包版本 在返回所有的版本包 便于展示
def find_max_revison(result, root_type, plat):
    max_svn = 0
    max_new_message = {}
    svn_list = {}

    for file_message in result:
        for path, platform_info in file_message.items():
            if root_type in path:
                for plat_form, bundle_info in platform_info.items():
                    if bundle_info['svn'] not in svn_list:
                        svn_list[bundle_info['svn']] = True
                    if plat == plat_form:
                        if max_svn < int(bundle_info['svn']):
                            max_svn = int(bundle_info['svn'])
                            max_new_message = bundle_info

    return max_new_message, svn_list

#
def get_svn_info(result, svn_number):
    revison_url = ''
    for file_message in result:
        for path, platform_info in file_message.items():
            for plat_form, bundle_info in platform_info.items():
                if int(bundle_info['svn']) == svn_number:
                    revison_url =  bundle_info['revison_url']
                    break
    return revison_url


# 预测的涉及的包的信息展示
def concat_revison_pakcage(result, svn_list, msvn_nmber):
    message = ''
    if len(svn_list) <= 1:
       return message
    for svn, info in svn_list.items():
        print('[Test]svn: ',svn)
        if int(svn) < int(msvn_nmber):
           if get_svn_info(result, msvn_nmber) != '':
               info = '[[版本'+svn+'|'+get_svn_info(result, msvn_nmber)+']] '
               if len(message + info) < 30000:
                   message += info
    return message



def merge_content(result, root, platform):
    content = ' '
    color_message = jx3m_page_Platform['color_green']  # 默认是绿色 全部包括
    new_message, svn_info = find_max_revison(result, root, platform)
    if new_message:
        preview_message = concat_revison_pakcage(result_total, svn_info, new_message['svn'])
        print('preview_message: ',preview_message)
        package_size = new_message['package_size']
        if 'MB' in package_size:
            package_size = package_size.replace('MB', '')
        elif 'KB' in package_size:
            package_size = round(int(package_size.replace('MB', ''))/1024, 2)
        else:
            package_size = round(int(package_size)/1024, 2)

        if preview_message != '':
            print('存在预测更新包信息 更换颜色')
            color_message = jx3m_page_Platform['color_yellow']

        if '/branches-rel' in root:
            root = root.replace('/branches-rel', '')

        root_platform = root + ' ' +platform
        if root == '/trunk':
            print('trunk file mesage concat')

            mesage_temp = color_message.format('版本包:') + '['+new_message['svn'] + '('+ str(package_size)+'MB)|' + new_message['revison_url'] + ']'
            # content = '|'+root_platform+'|[版本包' + new_message['svn'] + '('+ str(package_size)+'MB)|' + new_message['revison_url'] + ']|' + ' |' + preview_message + ' |\n'
            content = '|'+root_platform+'|'+mesage_temp+'|' + ' |' + preview_message + ' |\n'
        else:
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
    # 主干获取bundle测试通过
    # print('begin: ',time.time())
    trunk_path_to_bundle, txpublish_path_to_bundle, hotfix_path_to_bundle = analy.get_aba_bundle_dict()
    # print('end: ', time.time())
    jx3m = JX3M()
    single_number_assets = jx3m.get_single_number_assets()
    total_len = len(single_number_assets)
    print('[Test]当前处理的提交单长度为: ', total_len)

    count = 1

    for single_number, root_info in single_number_assets.items():
        print('[Test]当前正在分析第' + str(count) + '个提交单,单号为:' + single_number)

        # 获取当前单的所有信息 文件对应bundle 或者 没有找到bundle的文件列表
        result_total = analy_single_number(trunk_path_to_bundle, txpublish_path_to_bundle, hotfix_path_to_bundle, root_info)
        # for file_info in result_total:
        #     for file, platform in file_info.items():
        #         print('file: ', file)
        #         print('platform: ', str(platform))
        is_txpublish_exit = False
        is_total_exit = False

        details_url = jx3m_page_Platform['details_url'].format(single_number)
        txpublish_url = jx3m_page_Platform['txpublish_url'].format(single_number)
        item_tile = '*更新包大小预测结果[[详情|' + details_url + ']]*\n|分类|安装包|更新包|预测包|\n'
        txpublish_title = '[此单分支文件bundle包大小预测详细信息点击此链接|' + txpublish_url + ']'

        # 向平台提交数据
        jx3m.commit_single_number_assetinfo(single_number, result_total)

        # 获取主干 分支 hotfix android ios 是否有最新版本出来
        content_message = ''
        trunk_message = ''
        txpublish_message = ''
        hotfixmessage = ''
        color_content = '注意：[版本包]绿色字体表示此单所提交的文件均在对应的版本包中 黄色字体表示此单某些文件不在此版本包中,相对应预测包信息可大概估计文件下一版本打包时会影响的bundle大小'

        if single_number_assets[single_number]['trunk']:
            is_total_exit = True
            trunk_message += check_out_index(content_message, merge_content(result_total, '/trunk', 'Android'))
            trunk_message += check_out_index(content_message, merge_content(result_total, '/trunk', 'iOS'))
            # print('trunk message: ', trunk_message)

        if single_number_assets[single_number]['txpublish']:
            is_txpublish_exit = True
            txpublish_message += check_out_index(content_message, merge_content(result_total, '/branches-rel/tx_publish', 'Android'))
            txpublish_message += check_out_index(content_message, merge_content(result_total, '/branches-rel/tx_publish', 'iOS'))
            # print('txpublish message: ', txpublish_message)

        if single_number_assets[single_number]['tx_publish_hotfix']:
            hotfixmessage += check_out_index(content_message, merge_content(result_total, '/branches-rel/tx_publish_hotfix', 'Android'))
            hotfixmessage += check_out_index(content_message, merge_content(result_total, '/branches-rel/tx_publish_hotfix', 'iOS'))
            # print('tx_publish_hotfix  message: ', hotfixmessage)
        if is_total_exit:
            finall_content = item_tile + trunk_message+txpublish_message+hotfixmessage
            if is_txpublish_exit:
                finall_content = item_tile + trunk_message+txpublish_message+hotfixmessage+txpublish_title
            finall_content = finall_content +'\n' + color_content
            jx3m.update_comment(single_number,finall_content)
        print('content_message: ', )

        count = count + 1




