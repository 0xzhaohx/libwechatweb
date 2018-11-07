#!/usr/bin/python2.7
# -*- coding: UTF-8 -*-
'''
Created on 2018年3月25日

@author: zhaohongxing
'''
import os

class WechatConfig(object):

    def __init__(self):
        self.__app_home = ("%s\\.wechat")%(os.path.expanduser('~'))
        #new
        self.customFace = "%s\\customface"%(self.__app_home)
        self.imageRecive = "%s\\imageRec"%(self.__app_home)
        self.__default_head_icon = './resource/images/default.png'
    
    def getAppHome(self):
        return self.__app_home
    
    def getDefaultIcon(self):
        return self.__default_head_icon