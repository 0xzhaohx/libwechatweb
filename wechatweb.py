#!/usr/bin/python2.7
# -*- coding: UTF-8 -*-
'''
Created on 2018年3月25日

@author: zhaohongxing
'''

import re
import os
import logging
from api.wechatwebapi import WeChatAPI

class WeChatWeb(object):
    
    def __new__(self):
        logging.debug("WeChatWeb __new__")
        if not hasattr(self, "instance"):
            self.instance = super(WeChatWeb,self).__new__(self)
        return self.instance
    
    def __init__(self):
        self.hosts = {
            "weixin.qq.com":{
                'login':'login.weixin.qq.com',
                'file':'file.wx.qq.com',
                'push':'webpush.weixin.qq.com'
            },
            "wx2.qq.com":{
                'login':'login.wx2.qq.com',
                'file':'file.wx2.qq.com',
                'push':'webpush.wx2.qq.com'
            },
            "wx8.qq.com":{
                'login':'login.wx8.qq.com',
                'file':'file.wx8.qq.com',
                'push':'webpush.wx8.qq.com'
            },
            "qq.com":{
                'login':'login.wx.qq.com',
                'file':'file.wx.qq.com',
                'push':'webpush.wx.qq.com'
            },
            "wechat.com":{
                'login':'login.web.wechat.com',
                'file':'file.web.wechat.com',
                'push':'webpush.web.wechat.com'
            },
            "web2.wechat.com":{
                'login':'login.web2.wechat.com',
                'file':'file.web2.wechat.com',
                'push':'webpush.web2.wechat.com'
            }
        }
        '''
        self.user_home = os.path.expanduser('~')
        self.app_home = self.user_home + '\\.wechat'
        self.cache_home__ = ("%s\\cache"%(self.app_home))
        self.cache_image_home__ = "%s\\image"%(self.cache_home)
        '''
        #new
        self.app_home = ("%s\\.wechat")%(os.path.expanduser('~'))
        self.customFace = "%s\\customface"%(self.app_home)
        self.imageRecive = "%s\\imageRec"%(self.app_home)
        self.default_head_icon = './resource/images/default.png'
        
        logging.basicConfig(filename='%s\\wechat.log'%self.app_home,level=logging.DEBUG,format='%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s')
        self.status = -1#登陸成功與否
        self.__webchatwebapi = WeChatAPI()
        self.webchatwebapi = self.__webchatwebapi
        #the user who had login
        self.__user = []
        #會話联系人列表
        self.__chat_list = []
        #聯系人列表（包含會話列表）
        self.__friend_list = []
        self.timeout = 30
        self.version='0.1'
        self.wxversion = 'v2'
    
    def generate_qrcode(self):
        '''
        
        '''
        return self.__webchatwebapi.generate_qrcode()

    def webwx_stat_report(self):
        self.__webchatwebapi.webwx_stat_report()
    
    def wait4login(self,tip=1):
        return self.__webchatwebapi.wait4login(tip)
    '''
    def get_redirect_url(self):
        return self.__webchatwebapi.get_redirect_url()
    '''
    def login(self):
        '''
        return:
            <error>
                <ret>0</ret>
                <message>OK</message>
                <skey>xxx</skey>
                <wxsid>xxx</wxsid>
                <wxuin>xxx</wxuin>
                <pass_ticket>xxx</pass_ticket>
                <isgrayscale>1</isgrayscale>
            </error>
        '''
        return self.__webchatwebapi.login()

    '''
    return a mini list of chat 
    '''
    def webwx_init(self):
        data = self.__webchatwebapi.webwx_init()
        #此处的__user主要是在__webwxstatusnotify()中用
        self.__user = data['User']
        #TODO FIX BUG
        self.__chat_list = data['ContactList']
        #download and setup logined user head img
        self.webwx_get_icon(self.__user['UserName'], self.__user['HeadImgUrl'])
        self.__webwxstatusnotify()
        return data

    def __webwxstatusnotify(self):
        return self.__webchatwebapi.webwxstatusnotify(self.__user)

    def webwx_get_icon(self, user_name, img_url):
        self.__webchatwebapi.webwx_get_icon(user_name, img_url)
            
    def webwx_get_head_img(self,user_name,head_img_url):
        '''
        #用於取群圖標
        '''
        self.__webchatwebapi.webwx_get_head_img(user_name, head_img_url)

    def webwx_get_contact(self):
        '''
        #賬號類型：
        #
        #VerifyFlag
        #
        '''
        contacts_dict = self.__webchatwebapi.webwx_get_contact()
        #see #webwx_batch_get_contact()
        self.__friend_list.extend(contacts_dict['MemberList'])
        #self.__friend_count += int(contacts_dict['MemberCount'])
        #TODO download the user head icon
        for member in self.__friend_list:
            user_name = member['UserName']
            head_img_url = member['HeadImgUrl']
            if not user_name or not head_img_url:
                continue
            if user_name.startswith('@'):
                ##self.webwx_get_icon(user_name, head_img_url)
                pass
            elif user_name.startswith('@@'):
                ##self.webwx_get_head_img(user_name, head_img_url)
                pass
            else:
                pass
        return contacts_dict['MemberList']
    '''
    #調用完webwx_init得到部分的有過聯天記錄的用户，再調用webwx_batch_get_contact可以護得完整的有過聯天記錄的用户列表
    params:
    1.
        params = {
            'BaseRequest': self.base_request,
            'Count': 1,
            'List': [
                {

                    'UserName': '',
                    'EncryChatRoomId': ''
                }

            ]
        }
    ###################################################
    2.
        params = {
            'BaseRequest': self.base_request,
            'Count': 1,
            'List': [
                {

                    'UserName': '',#群name.如：@@xxxxxx
                    'ChatRoomId': ''
                }

            ]
        }
    '''
    def webwx_batch_get_contact(self, params):
        dictt = self.__webchatwebapi.webwx_batch_get_contact(params)
                   
        return dictt
        
    def sync_check(self,host=None):
        '''
            response body: wechat.synccheck={retcode:"xxx",selector:"xxx"}
            retcode:
                0:success
                1100:你在手机上登出了微信
                1101:你在其他地方登录了 WEB 版微信
                1102:你在手机上主动退出了
            selector:
                0:nothing
                2:new message?发送消息返回结果
                4:朋友圈有动态
                6:有消息返回结果
                7:webwxsync? or 进入/离开聊天界面?
                
        '''
        response = self.__webchatwebapi.sync_check(host)
        
        pm = re.search(r'window.synccheck={retcode:"(\d+)",selector:"(\d+)"}', response)
        if pm:
            return (pm.group(1), pm.group(2))
        else:
            return (-1,-1)

    def webwx_sync(self):
        '''
        BaseResponse
        AddMsgCount:新增消息数
        AddMsgList：新增消息列表
        ModContactCount: 变更联系人数目
        ModContactList: 变更联系人列表
        SyncKey:新的synckey列表
        '''
        return self.__webchatwebapi.webwx_sync()
    
    def webwx_send_emoticon(self,message):
        return self.__webchatwebapi.webwx_send_emoticon(message)
    
    def webwx_send_msg(self,message):
        return self.__webchatwebapi.webwx_send_msg(self.__user,message)
    
    def webwx_send_msg_img(self,message):
        return self.__webchatwebapi.webwx_send_msg_img(self.__user,message)
    
    def webwx_send_app_msg(self,message):
        return self.__webchatwebapi.webwx_send_app_msg(self.__user,message)
    
    def webwx_revoke_msg(self,message):
        return self.__webchatwebapi.webwx_revoke_msg(self.__user,message)
    
    def webwx_upload_media(self,dest_user,upload_file):
        return self.__webchatwebapi.webwx_upload_media(self.__user,dest_user, upload_file)
    
    def webwx_get_msg_img(self,message_id,media_type="jpg"):
        '''
        :desc 根据MSG_ID下載圖片
        '''
        data = self.__webchatwebapi.webwx_get_msg_img(message_id, media_type)
        return data
    
    def webwx_create_chatroom(self,member_list):
        '''
        :param member_list[{UserName:"@xxxxxxxx"}]
        '''
        response = self.__webchatwebapi.webwx_create_chatroom(member_list)
        return response
    
    def webwx_update_chatroom(self,params):
        '''
        :param params format:{"NewTopic":"xxx","ChatRoomName":"xxx","BaseRequest":"xxxx"}
        '''
        response = self.__webchatwebapi.webwx_update_chatroom(params)
        return response
    
    def getWebchatWebAPI(self):
        return self.__webchatwebapi
    
    def getUser(self):
        return self.__user
    
    def getChatContacts(self):
        return self.__chat_list
    
    def addChatContact(self,i,contact):
        self.__chat_list[i] = contact
    
    def appendChatContact(self,contact):
        self.__chat_list.append(contact)
        
    def getFriends(self):
        return self.__friend_list
    
    def appendFriend(self,friend):
        self.__friend_list.append(friend)

    def update_chat_contact(self,i,contact):
        self.__chat_list[i] = contact
        
    @DeprecationWarning
    def update_friend(self,i,contact):
        self.__friend_list[i] = contact
    
    
if __name__ =="__main__":
    api = WeChatAPI()
    uuid = api.__get_uuid()
    print("__get uuid success")
    api.generate_qrcode()
    print("enerate_qrcode success")
    res = api.wait4login()
    if not api.redirect_uri:
        res = api.wait4login(0)
        print("wait4login:")
        print(res)
    res = api.login()
    init_response = api.webwx_init()
    #print(init_response)
    #api.webwx_status_notify()
    api.webwx_get_contact()
    api.sync_check()
    #da = wechatweb.webwx_sync()





