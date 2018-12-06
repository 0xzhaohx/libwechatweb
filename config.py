#!/usr/bin/python2.7
# -*- coding: UTF-8 -*-
'''
Created on 2018年3月25日

@author: zhaohongxing
'''
import os

class WechatConfig(object):

    def __init__(self):
        self.__app_home = ("%s%s.wechat")%(os.path.expanduser('~'),os.sep)
        #new
        self.customFace = "%s%scustomface"%(self.__app_home,os.sep)
        self.imageRecive = "%s%simageRec"%(self.__app_home,os.sep)
        self.__default_head_icon = './resource/images/default.png'
    
    def getAppHome(self):
        return self.__app_home
    
    def getDefaultIcon(self):
        return self.__default_head_icon