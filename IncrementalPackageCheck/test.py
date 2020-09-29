# coding: utf8

from Jira_model import JX3M
from analy_platform_model import Analy_Plat
from data_config import jx3m_page_Platform



# 提供在aba_bundle_dict中查找文件是否在bundle中
def check_asset_to_bundle_size(bundle_dict, asset_path, root_type):
    result_message = {}
    path = asset_path
    if not bundle_dict:
        print('[Test]bundle_dict is null')
        return
    if '/trunk' in path:
        path = path.replace('/trunk/JX3Pocket/', '')
    if '/branches-rel' in path:
        path = path.replace('/branches-rel/tx_publish/JX3Pocket/', '')

    for svn_timestamp, bundle_item in bundle_dict.items():
        split_result = svn_timestamp.split('-')
        for bundle_name, bundle_info in bundle_item.items():
            if path.upper() in bundle_info['filelist']:
                result_message['root'] = root_type
                result_message['file'] = asset_path
                result_message['platform'] = bundle_info['platform']
                result_message['svn'] = split_result[0]
                result_message['timestamp'] = split_result[1]
                result_message['bundle_name'] = bundle_name
                result_message['bundle_size'] = bundle_info['size']
                result_message['revison_url'] = jx3m_page_Platform['revison_url'].format(result_message['platform'], result_message['timestamp'])
                result_message['bundle_name_url'] = jx3m_page_Platform['bundle_url'].format(result_message['platform'], result_message['timestamp'], result_message['bundle_name'])
                break
    return result_message


def package_content(result_message):
    bundle_size = round(int(result_message['bundle_size'])/1024, 2)
    content_message = '|'+result_message['file']+'|['+str(result_message['svn']) +'|'+result_message['revison_url']+']|['+result_message['bundle_name'] + '|'+result_message['bundle_name_url']+']|'+str(bundle_size)+'KB|\n'
    # print('[Test]package_content内容为: ',content_message)
    return content_message

if __name__ == '__main__':
    jx3m = JX3M()
    single_number_assets = jx3m.get_single_number_assets()
    count = 1
    for single_number, root_info in single_number_assets.items():
        print('提交单个数为: '+str(count) +' 单号为:'+single_number)
        jx3m.update_comment(single_number, '')
        count = count + 1

    # 获取最新全包与更新包的aba_bundle信息

    # analy = Analy_Plat()
    # trunk_android_bundle, txpublish_android_bundle = analy.get_aba_bundle_dict()
    # print('[Test]当前获取的主干包个数为:'+str(len(trunk_android_bundle))+' 当前获取的分支包个数为:'+ str(len(txpublish_android_bundle)))
    #
    # # # 提供单号对应文件资源列表
    # jx3m = JX3M()
    #
    # single_number_assets = jx3m.get_single_number_assets()
    # total_len = len(single_number_assets)
    # print('[Test]当前处理的提交单长度为: ', total_len)
    # count = 1 # 记录单号列表进度
    #
    # # 查找主干文件预测更新包大小
    # # 合计所有分支文件所在bundle的大小
    # for single_number, root_info in single_number_assets.items():
    #     print('[Test]当前正在分析第'+str(count)+'个提交单,单号为:'+single_number)
    #     result_total = []
    #     is_txpublish_exit = False
    #     is_total_exit = False
    #     for root, file_lists in root_info.items():
    #         if root == 'trunk':
    #             for file in file_lists:
    #                 result = check_asset_to_bundle_size(trunk_android_bundle, file, 'trunk')
    #                 if result:
    #                     result_total.append(result)
    #
    #         if root == 'txpublish':
    #             for file in file_lists:
    #                 result = check_asset_to_bundle_size(txpublish_android_bundle, file, 'txpublish')
    #                 if not result:
    #                     result = check_asset_to_bundle_size(trunk_android_bundle, file, 'txpublish')
    #                     if result:
    #                         result_total.append(result)
    #                     else:
    #                         print('txpublish file not in pakckage')
    #
    #     # 分析完一个提交单则上报数据 上报备注
    #     content_type = '*更新包大小预测结果[[详情|http://j3m.rdev.kingsoft.net:8810/dashboard]]*\n'
    #     table_title = '|资源文件|版本信息|bundle名|bundle大小|\n'
    #
    #     # 标记分支要展示到页面的
    #     local_txpublish_content = ''
    #
    #     # 标记版本包的
    #     resivion_url = '查询的版本包有:'
    #
    #     # 标记是否有超出长度
    #     is_out_index = False
    #     content = '字符长度限制,未展示完全,具体内容请查看详情链接\n'
    #
    #     # 上报此单总的数据
    #     # if result_total:
    #     #     jx3m.commit_single_number_assetinfo(single_number, result_total)
    #
    #     for value in result_total:
    #         if value['svn'] not in resivion_url:
    #             is_total_exit = True
    #             resivion_url += '[版本'+value['svn']+'|'+value['revison_url'] +'] '
    #         print('[Test]value: ',value)
    #         if value['root'] == 'txpublish':
    #             is_txpublish_exit = True
    #             if len(local_txpublish_content + package_content(value)) > 30000:
    #                 is_out_index = True
    #                 break
    #             local_txpublish_content += package_content(value)
    #
    #     if is_txpublish_exit:
    #         print('[Test]此单存在分支文件提交')
    #         upload_message = ''
    #         if is_out_index:
    #             upload_message = content_type + table_title + resivion_url + local_txpublish_content + content
    #         else:
    #             upload_message = content_type + table_title + resivion_url + local_txpublish_content
    #         jx3m.update_comment(single_number, content_type + table_title + resivion_url + local_txpublish_content)
    #     else:
    #         if is_total_exit:
    #             print('resivion_url: ', resivion_url)
    #             jx3m.update_comment(single_number, content_type + resivion_url)
    #     count = count + 1

