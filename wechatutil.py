#!/usr/bin/python3
# -*- coding: UTF-8 -*-
'''
Created on 2018年11月2日

@author: zhaohongxing

'''

'''
1.ContactFlag:
    1是好友，值为3是公众号
2."UserName" 用户名称:
    以"@"开头为好友，以"@@"为群组
3."Sex": 
    性别，0-未设置（公众号、保密），1-男，2-女
4."StarFriend": 是否为星标朋友  0-否  1-是
'''
def decode_data(data):
    """
    @brief      decode array or dict to utf-8
    @param      data   array or dict
    @return     utf-8
    """
    if isinstance(data, dict):
        rv = {}
        '''
        for key, value in data.iteritems():
        '''
        for key, value in data.items():
            if isinstance(key, str):
                #key = key.encode('utf-8') python2
                pass
                #key = key.encode("utf-8")
            rv[key] = decode_data(value)
        return rv
    elif isinstance(data, list):
        rv = []
        for item in data:
            item = decode_data(item)
            rv.append(item)
        return rv
    elif isinstance(data, str):
        return data
    else:
        return data
    
def unicode(s):
    return s;