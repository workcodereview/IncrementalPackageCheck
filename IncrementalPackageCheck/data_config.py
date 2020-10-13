# coding: utf8

# 构建平台取aba_bundle信息路径
analy_platform = {
    'package_url': 'http://10.11.10.86/list/resources_package',
    'ababundle_url': 'http://10.11.10.86/download/resource_package'
}

# 向jx3m_page平台写备注信息
jx3m_page_Platform = {
    'username': 'svnchecker',
    'password': 'mimashi1101',
    'jx3m_page_url': 'http://jx3m.rdev.kingsoft.net:8881/rest/api/2/issue/{0}/comment',
    'record_url': 'http://jx3m.rdev.kingsoft.net:8881/rest/api/2/issue/{0}',
    'URL_SEARCH': 'http://jx3m.rdev.kingsoft.net:8881/rest/api/2/search',
    'revison_url': 'http://10.11.10.86/resource/package/false/{0}/{1}/tab',
    'bundle_url': 'http://10.11.10.86/resource/package/false/{0}/{1}/package_list/files/other/{2}///',
    'upload_url': 'http://jx3mtestup.rdev.kingsoft.net/upload/sync/update_package_info/{0}',
    'details_url': 'http://10.11.10.86/jira/size/{0}/true',
    'txpublish_url': 'http://10.11.10.86/jira/size/{0}/false',
    'color_green': '{{color:#14892c}}{0}{{color}}',
    'color_orige': '{{color:#f79232}}{0}{{color}}',
    'total_single_number_url': 'http://jx3m.rdev.kingsoft.net:8881/rest/api/2/project/JX3M/versions'
}

# 用于访问qb平台 获取信息
qb_config= {
    'username': 'zhangyin',
    'password': 'Zy0297.Zyd02',
    'trunk_url': 'http://j3m.rdev.kingsoft.net:8810/overview/2021',
    'txpublish_url': 'http://j3m.rdev.kingsoft.net:8810/overview/2011'
}

svn_config = {
    'username': 'scm_builder_jx3m',
    'password': '_ZMvNHvP0C',
    'url': 'svn://xsjreposvr3.rdev.kingsoft.net/JX3M',
}


redis_config = {
    'host': '10.11.10.143',
    'port': 6379,
    'password': 'yourpassword'
}

