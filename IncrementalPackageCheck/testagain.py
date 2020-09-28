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
    return_result = []
    single_number_result = {}

    for root_type, file_list in root_message.items():
        for file in file_list:
            print('[Test]当前分析的文件为: ',file)
            android_result = {}
            ios_result = {}

            if file not in single_number_result:
                single_number_result[file] = {}

            if root_type == 'trunk':
                android_result = check_asset_bundle(trunk_bundle['Android'], file, root_type, 'Android')
                ios_result = check_asset_bundle(trunk_bundle['iOS'], file, root_type, 'iOS')
            elif root_type == 'txpublish':
                android_result = check_asset_bundle(txpublish_bundle['Android'], file, root_type, 'Android')
                ios_result = check_asset_bundle(txpublish_bundle['iOS'], file, file, 'iOS')
                if not android_result and not ios_result:
                    android_result = check_asset_bundle(txpublish_bundle['Android'], file, root_type, 'Android')
                    ios_result = check_asset_bundle(txpublish_bundle['iOS'], file, root_type, 'iOS')
            elif root_type == 'tx_publish_hotfix':
                android_result = check_asset_bundle(hotfix_bundle['Android'], file, root_type, 'Android')
                ios_result = check_asset_bundle(hotfix_bundle['iOS'], file, root_type, 'iOS')

            if android_result:
                print('[Test]Android 有返回数据',str(android_result))
                single_number_result[file]['Android'] = android_result
            if ios_result:
                print('[Test]iOS 有返回数据',str(ios_result))
                single_number_result[file]['iOS'] = ios_result

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
                    if plat_form == plat:
                        if max_svn < int(bundle_info['svn']):
                            max_svn = int(bundle_info['svn'])
                            max_new_message = bundle_info
                            svn_list[bundle_info['svn']] = bundle_info['revison_url'] # 保存所有小于最新的包版本
    if max_svn != 0:
        svn_list.pop(str(max_svn))
    return max_new_message, svn_list



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
    print('[Test]get bundle info begin:',time.time())
    analy = Analy_Plat()
    # 主干获取bundle测试通过
    trunk_path_to_bundle, txpublish_path_to_bundle, hotfix_path_to_bundle = analy.get_aba_bundle_dict()
    print('[Test]get bundle info end:', time.time())
    jx3m = JX3M()
    # single_number_assets = jx3m.get_single_number_assets()
    single_number_assets = jx3m.get_single_number_assets()
    print('[Test]get single number info end:', time.time())
    print('单号长度: ',len(single_number_assets))

    count = 1

    begin_time = time.time()
    for single_number, root_info in single_number_assets.items():
        print('[Test]当前正在分析第' + str(count) + '个提交单,单号为:' + single_number)
        # if count == 6:
        #     break
        # 获取当前单的所有信息 文件对应bundle 或者 没有找到bundle的文件列表
        result_total = analy_single_number(trunk_path_to_bundle, txpublish_path_to_bundle, hotfix_path_to_bundle, root_info)
        # print('result_total: ',str(result_total))

        is_txpublish_exit = False
        is_total_exit = False

        details_url = jx3m_page_Platform['details_url'].format(single_number)
        txpublish_url = jx3m_page_Platform['txpublish_url'].format(single_number)
        item_tile = '*更新包大小预测结果[[详情|' + details_url + ']]*\n|分类|安装包|更新包|预测包|\n'
        txpublish_title = '[此单分支文件bundle包大小预测详细信息点击此链接|' + txpublish_url + ']'

        # 获取主干 分支 hotfix android ios 是否有最新版本出来
        content_message = ''
        trunk_message = ''
        txpublish_message = ''
        hotfixmessage = ''
        finall_content = ''
        color_content = '注意：[版本包]绿色字体表示此单所提交的文件均在对应的版本包中 橙色字体表示此单某些文件不在此版本包中,相对应预测包信息可大概估计文件下一版本打包时会影响的bundle大小'

        if single_number_assets[single_number]['trunk']:
            trunk_message += check_out_index(content_message, merge_content(result_total, '/trunk', 'Android'))
            trunk_message += check_out_index(content_message, merge_content(result_total, '/trunk', 'iOS'))

        if single_number_assets[single_number]['txpublish']:
            txpublish_message += check_out_index(content_message, merge_content(result_total, '/branches-rel/tx_publish', 'Android'))
            txpublish_message += check_out_index(content_message, merge_content(result_total, '/branches-rel/tx_publish', 'iOS'))

        if single_number_assets[single_number]['tx_publish_hotfix']:
            hotfixmessage += check_out_index(content_message, merge_content(result_total, '/branches-rel/tx_publish_hotfix', 'Android'))
            hotfixmessage += check_out_index(content_message, merge_content(result_total, '/branches-rel/tx_publish_hotfix', 'iOS'))

        if trunk_message or txpublish_message or hotfixmessage:
            is_total_exit = True
        if txpublish_message:
            is_txpublish_exit = True

        if is_total_exit:
            # 向平台提交数据
            jx3m.commit_single_number_assetinfo(single_number, result_total)
            finall_content = item_tile + trunk_message+txpublish_message+hotfixmessage
            if is_txpublish_exit:
                finall_content = item_tile + trunk_message+txpublish_message+hotfixmessage+txpublish_title
            finall_content = finall_content +'\n' + color_content
            print('finall_content: ',finall_content)
            jx3m.update_comment(single_number,finall_content)
        else:
            finall_content = '*更新包大小预测结果*\n'+'此单当前文件暂未有打包信息,等待后续版本包信息再进行预测\n'
            jx3m.update_comment(single_number, finall_content)

        count = count + 1
    print('提交单数量：',str(count))
    print('[Test]analy single number end: ', str(begin_time - time.time()))




