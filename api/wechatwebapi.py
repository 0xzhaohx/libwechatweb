#!/usr/bin/python2.7
# -*- coding: UTF-8 -*-
'''
Created on 2018年3月25日

@author: zhaohongxing
'''

import random
import time
import urllib
import requests
import re
import xml.dom.minidom
import json
import os
import hashlib
import mimetypes
import logging
import wechatutil

class WeChatAPI(object):
    __HOSTS = {
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
    __USER_AGENTS = [ 
        'Mozilla/5.0 (X11; Linux x86_64)', 
        'AppleWebKit/537.36 (KHTML, like Gecko)',
        'Chrome/65.0.3325.181',
        'Safari/537.36'
    ]
    
    def __init__(self):
        #new
        self.app_home = ("%s\\.wechat")%(os.path.expanduser('~'))
        self.customFace = "%s\\customface"%(self.app_home)
        self.imageRecive = "%s\\imageRec"%(self.app_home)
        self.hosts = self.__HOSTS["weixin.qq.com"]
        logging.basicConfig(filename='./wechatwebapi.log',level=logging.DEBUG,format='%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s')
        self.__appid = 'wx782c26e4c19acffb'
        self.__uuid = ''
        self.__redirect_uri = None
        self.__login_icon = True
        self.__skey = ''
        #wxsid:weixin session id
        self.__sid = ''
        #wxuin: weixin user identity number
        self.__uin = ''
        #pass_ticket: 通关文牒
        self.__pass_ticket = ''
        self.__is_grayscale = 0
        self.__base_request = {}
        self.__sync_key_dic = []
        self.__sync_key = ''
        # device_id: 登录手机设备
        # web wechat 的格式为: e123456789012345 (e+15位随机数)
        # mobile wechat 的格式为: A1234567890abcde (A+15位随机数字或字母)
        self.__device_id = 'e' + repr(random.random())[2:17]
        self.__fun = 'new'
        self.__lang = 'zh_TW'
        self.timeout = 30
        self.__session = requests.session()
        self.__user_agent = self.__USER_AGENTS[random.randint(0,len(self.__USER_AGENTS)-1)]
        self.version='0.1'
        self.wxversion = 'v2'
        
    def get_redirect_url(self):
        return self.__redirect_uri
    
    def resetdeviceid(self):
        #self.__base_request["DeviceID"]='e%s'%repr(random.random())[2:17]
        pass
        
    def __get_uuid(self):
        url = "https://login.wx.qq.com/jslogin";
        params = {
            'appid': self.__appid,
            'redirect_uri': 'https://wx.qq.com/cgi-bin/mmwebwx-bin/webwxnewloginpage',
            'fun': self.__fun,
            'lang': self.__lang,
            '_': int(time.time())
        }
        '''for python2
        url = url + "?" + urllib.urlencode(params)
        '''
        url = url + "?" + urllib.parse.urlencode(params)
        response = self.__get(url)
        return response


    def __set_uuid(self,regx,data):
        pm = re.search(regx, data)
        if pm:
            #code = pm.group(1)
            self.__uuid = pm.group(2)
            return True
        else:
            return False

    def generate_qrcode(self):
        response = self.__get_uuid()
        regx = r'wechat.QRLogin.code = (\d+); wechat.QRLogin.uuid = "(\S+?)"'
        if self.__set_uuid(regx,response):
            pass
        else:
            regx = r'window.QRLogin.code = (\d+); window.QRLogin.uuid = "(\S+?)"'
            if self.__set_uuid(regx, response):
                pass
        url = "https://login.weixin.qq.com/qrcode/" + self.__uuid;
        params = {
            't': 'webwx',
            '_': int(time.time())
        }
        data = self.__post(url, params, stream=True)

        image = self.app_home+"/qrcode.jpg"
        with open(image, 'wb') as image:
            image.write(data)
            return image

    def webwx_stat_report(self):
        url = "https://wx.qq.com/cgi-bin/mmwebwx-bin/webwxstatreport?fun=new&lang="+self.__lang;
        #self.resetdeviceid()
        params = {
            'BaseRequest': self.__base_request,
            'Count': 0,
            'List': []
        }
        response = self.__post(url, params)

        #print(data)
        return response
    
    def wait4login(self,tip=1):
        '''
        tip = 0 已扫描
        tip = 1 未扫描
        return code
        408 timeout
        200 登陸成功
        201 己掃描
        '''
        url = "https://login.weixin.qq.com/cgi-bin/mmwebwx-bin/login" + "?loginicon="+str(self.__login_icon)+"&tip=" + str(tip) + "&uuid=" + self.__uuid + "&_" + str(int(time.time()))
        response = self.__get(url)
        data = response.replace("\n","")
        data = data.replace("\r","")
        pm = re.search(r'wechat.code=(\d+);', data)
        if not pm:
            pm = re.search(r'window.code=(\d+);', data)
        code = pm.group(1)
        if code == '201':
            pass
        elif code == '200':
            pm = re.search(r'wechat.redirect_uri="(\S+?)";', data)
            if not pm:
                pm = re.search(r'window.redirect_uri="(\S+?)";', data)
            if not pm:
                code = -1
            self.__redirect_uri = "%s&fun=%s&version=v2"%(pm.group(1),self.__fun)
        elif code == '408':
            print("error 408")
        else:
            code = -9999
            print("unknow error")
        return code

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
        response = self.__get(self.__redirect_uri)
        doc = xml.dom.minidom.parseString(response)
        root = doc.documentElement
        for node in root.childNodes:
            for cn in node.childNodes:
                if node.nodeName == 'ret':
                    if cn.data != "0":
                        return False
                elif node.nodeName == 'skey':
                    self.__skey = cn.data
                elif node.nodeName == 'wxsid':
                    self.__sid = cn.data
                elif node.nodeName == 'wxuin':
                    self.__uin = cn.data
                elif node.nodeName == 'pass_ticket':
                    self.__pass_ticket = cn.data
                elif node.nodeName == 'isgrayscale':
                    self.__is_grayscale = cn.data

        self.__base_request = {
            'Uin': int(self.__uin),
            'Sid': str(self.__sid),
            'Skey': str(self.__skey),
            'DeviceID': self.__device_id,
        }
        return True

    def webwx_init(self):
        url = "https://wx.qq.com/cgi-bin/mmwebwx-bin/webwxinit" + \
              '?pass_ticket=%s&r=%s&lang=%s' % (
                  self.__pass_ticket, int(time.time()), self.__lang
              )
        #self.resetdeviceid()
        params = {
            'BaseRequest': self.__base_request
        }
        headers = {
            'User-Agent': self.__user_agent,
            'Content-Type': 'application/json; charset=UTF-8',
            'Connection': 'keep-alive',
            'Referer': 'https://wx.qq.com/'
        }

        response = self.__post(url=url, data=json.dumps(params, ensure_ascii=False).encode('utf8'), headers=headers)
        chats_dict = json.loads(response, object_hook=wechatutil.decode_data)
        self.__update_sync_key(chats_dict)
        return chats_dict

    def webwxstatusnotify(self,user):
        url = "https://wx.qq.com/cgi-bin/mmwebwx-bin/webwxstatusnotify" + \
              '?pass_ticket=%s' % (
                  self.__pass_ticket
              )
        #self.resetdeviceid()
        params = {
            'BaseRequest': self.__base_request,
            'Code' : 3,
            'FromUserName': user['UserName'],
            'ToUserName': user['UserName'],
            'ClientMsgId': int(time.time())
        }
        response = self.__post_json(url, params)
        return response

    def webwx_get_icon(self, user_name, head_img_url):
        url = 'https://wx.qq.com%s'%(head_img_url)
        streamdata = self.__get(url,stream=True)
        if not streamdata and ( len(streamdata) == 0 or b'' == streamdata or '' == streamdata ):
            logging.warning("stream data of %s is null"%head_img_url)
        else:
            image = '%s\\%s.jpg'%(self.customFace,user_name)
            with open(image, 'wb') as image:
                image.write(streamdata)
            
    def webwx_get_head_img(self,user_name,head_img_url):
        '''
        #用於取群圖標
        '''
        url = 'https://wx.qq.com%s'%(head_img_url)
        streamdata = self.__get(url,stream=True)
        if not streamdata:
            pass
        
        image = '%s\\%s.jpg'%(self.customFace,user_name)
        #image = '%s/heads/contact/%s.jpg'%(self.app_home,user_name)
        with open(image, 'wb') as image:
            image.write(streamdata)

    def webwx_get_contact(self):
        '''
        #賬號類型：
        #
        #VerifyFlag
        #
        '''
        url = "https://wx.qq.com/cgi-bin/mmwebwx-bin/webwxgetcontact" + \
              '?pass_ticket=%s&lang=%s' % (
                  self.__pass_ticket, self.__lang
              )
        #self.resetdeviceid()
        params = {
            'BaseRequest': self.__base_request
        }
        headers = {
            'user-agent': self.__user_agent,
            "content-type": "application/json; charset=UTF-8",
            'connection': 'keep-alive',
            "referer": "https://wx.qq.com/"
        }

        response = self.__post(url=url, data=json.dumps(params, ensure_ascii=False).encode('utf8'), headers=headers)
        contacts_dict = json.loads(response, object_hook=wechatutil.decode_data)
        
        return contacts_dict
    def webwx_batch_get_contact(self, params):
        '''
        調用完webwx_init得到部分近期有過聯天的用户，再調用webwx_batch_get_contact可以護得完整的有過聯天記錄的用户列表
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
        
        params['BaseRequest']= self.__base_request
        url = "https://wx.qq.com/cgi-bin/mmwebwx-bin/webwxbatchgetcontact" + \
              '?type=ex&r=%s&pass_ticket=%s' % (
                  int(time.time()),self.__pass_ticket
              )

        response = self.__post(url=url, data=json.dumps(params, ensure_ascii=False).encode('utf8'))
        dictt = json.loads(response, object_hook=wechatutil.decode_data)
                   
        return dictt

    def sync_check(self,host=None):
        '''
            response body:wechat.synccheck={retcode:"xxx",selector:"xxx"}
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
        if not host:
            host = "https://webpush.wx.qq.com/cgi-bin/mmwebwx-bin/synccheck"
        params = {
            'r': int(time.time()),
            'skey': str(self.__skey),
            'sid': str(self.__sid),
            'uin': int(self.__uin),
            'deviceid': 'e%s'%repr(random.random())[2:17],
            'synckey': str(self.__sync_key),
            '_': int(time.time())
        }

        '''for python2
        url = host + "?" + urllib.urlencode(params)
        '''
        url = host + "?" + urllib.parse.urlencode(params)
        response = self.__get(url)
        return response

    def __update_sync_key(self,resp):
        self.__sync_key_dic = resp['SyncKey']
        '''
        def foo(x):
            return str(x['Key']) + '_' + str(x['Val'])
        self.__sync_key = '|'.join([foo(keyVal) for keyVal in self.__sync_key_dic['List']])
        '''
        self.__sync_key = '|'.join(["%s_%s"%(k,v) for k,v in self.__sync_key_dic['List']])
        
    def webwx_sync(self):
        '''
        BaseResponse
        AddMsgCount:新增消息数
        AddMsgList：新增消息列表
        ModContactCount: 变更联系人数目
        ModContactList: 变更联系人列表
        SyncKey:新的synckey列表
        '''
        url = "https://wx.qq.com/cgi-bin/mmwebwx-bin/webwxsync" + \
            '?sid=%s&skey=%s&pass_ticket=%s' % (
                self.__sid, self.__skey, self.__pass_ticket
            )
        #self.resetdeviceid()
        params = {
            'BaseRequest': self.__base_request,
            'SyncKey':self.__sync_key_dic,
            'rr':~int(time.time())
        }
        headers = {
            'User-Agent': self.__user_agent,
            "Content-Type": "application/json; charset=UTF-8",
            "Referer": "https://wx.qq.com"
        }

        response = self.__post_json(url, params)
        dictt = json.loads(response, object_hook=wechatutil.decode_data)
        if dictt['BaseResponse']['Ret'] == 0:
            self.__update_sync_key(dictt)
        return response
    
    def webwx_send_emoticon(self,message):
        url = "https://wx.qq.com/cgi-bin/mmwebwx-bin/webwxsendemoticon" + \
              '?fun=sys&pass_ticket=%s' % (
                  self.__pass_ticket
              )
        local_id = client_msg_id = self.__get_client_msg_id()
        
        #self.resetdeviceid()
        params = {
            'BaseRequest': self.__base_request,
            'Msg': {
                "Type":message.message_type,
                "Content":message.content,
                "FromUserName":self.user['UserName'],
                "ToUserName":message.to_user_name,
                "LocalID":local_id,
                "ClientMsgId":client_msg_id,
            }
        }
        headers = {
            'User-Agent': "Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)",
            "Content-Type": "application/json; charset=UTF-8",
            "Referer": "https://wx.qq.com"
        }

        response = self.__post_json(url, params)
        return response
    
    def webwx_send_msg(self,user_from,message):
        url = "https://wx.qq.com/cgi-bin/mmwebwx-bin/webwxsendmsg" + \
              '?f=json&fun=async&pass_ticket=%s' % (
                  self.__pass_ticket
              )
        local_id = client_msg_id = self.__get_client_msg_id()
        headers = {
            "Content-Type": "application/json; charset=UTF-8"
        }
        #self.resetdeviceid()
        params = {
            'BaseRequest': self.__base_request,
            'Msg': {
                "Type":message.message_type,
                "FromUserName":user_from['UserName'],
                "ToUserName":message.to_user_name,
                "LocalID":local_id,
                "ClientMsgId":client_msg_id
            },
            "Scene":0
        }
        if message.message_type == 1:
            params['Msg']["Content"]=message.content
        elif message.message_type == 3:
            params['Msg']["MediaId"]=message.media_id
            params['Msg']["Content"]=""
        else:
            pass
        #print("senddd msg body:\r\n%s"%unicode(json.dumps(params, ensure_ascii=False).encode('utf8')))
        response = self.__post_json(url,params,headers=headers)
        return response
    
    def webwx_send_msg_img(self,user_from,message):
        url = "https://wx.qq.com/cgi-bin/mmwebwx-bin/webwxsendmsgimg" + \
              '?f=json&fun=async&pass_ticket=%s' % (
                  self.__pass_ticket
              )
        local_id = client_msg_id = self.__get_client_msg_id()
        headers = {
            "Content-Type": "application/json; charset=UTF-8"
        }
        #self.resetdeviceid()
        params = {
            'BaseRequest': self.__base_request,
            'Msg': {
                "Type":message.message_type,
                "FromUserName":user_from['UserName'],
                "ToUserName":message.to_user_name,
                "LocalID":local_id,
                "ClientMsgId":client_msg_id
            },
            "Scene":0
        }
        if message.message_type == 1:
            params['Msg']["Content"]=message.content
        elif message.message_type == 3:
            params['Msg']["MediaId"]=message.media_id
            params['Msg']["Content"]=""
        else:
            pass
        response = self.__post_json(url,params,headers=headers)
        return response
    
    def webwx_send_app_msg(self,user_from,message):
        url = 'https://wx.qq.com/cgi-bin/mmwebwx-bin/webwxsendappmsg' + \
              '?f=json&fun=async&pass_ticket=%s' % (
                  self.__pass_ticket
              )
        local_id = client_msg_id = self.__get_client_msg_id()
        headers = {
            "Content-Type": "application/json; charset=UTF-8"
        }
        #self.resetdeviceid()
        params = {
            'BaseRequest': self.__base_request,
            'Msg': {
                "Type":message.message_type,
                "FromUserName":user_from['UserName'],
                "ToUserName":message.to_user_name,
                "LocalID":local_id,
                "ClientMsgId":client_msg_id,
                "Content":message.content
            },
            "Scene":0
        }
        if message.message_type == 1:
            params['Msg']["Content"]=message.content
        elif message.message_type == 3:
            params['Msg']["MediaId"]=message.media_id
            params['Msg']["Content"]=""
        else:
            pass
        response = self.__post_json(url,params,headers=headers)
        return response
    
    def __get_client_msg_id(self):
        client_msg_id = "%d%s"%(int(time.time() * 1000) ,str(random.random())[:5].replace('.', ''))
        return client_msg_id
    
    def webwx_revoke_msg(self,user_from,message):
        url = "https://wx.qq.com/cgi-bin/mmwebwx-bin/webwxsendmsg" + \
              '?pass_ticket=%s' % (
                  self.__pass_ticket
              )
        local_id = client_msg_id = self.__get_client_msg_id()

        #self.resetdeviceid()
        params = {
            'BaseRequest': self.__base_request,
            'Msg': {
                "Type":message.message_type,
                "Content":message.content,
                "FromUserName":user_from['UserName'],
                "ToUserName":message.to_user_name,
                "LocalID":local_id,
                "ClientMsgId":client_msg_id,
            }
        }
        headers = {
            'Connection':'keep-alive',
            'Content-Type': 'application/json; charset=UTF-8',
            'Referer': 'https://wx.qq.com',
            'User-Agent': self.user_agent
        }

        response = self.__post_json(url=url, data=json.dumps(params, ensure_ascii=False).encode('utf8'), headers=headers)
        data = response.text
        response.close()
        return data
    
    def webwx_upload_media(self,user_from,user_to,upload_file):
        upload_file = str(upload_file)
        url = "https://file.wx.qq.com/cgi-bin/mmwebwx-bin/webwxuploadmedia?f=json"
        headers = {
            'Host':'file.wx.qq.com',
            'Origin': 'https://wx.qq.com'
        }
        options_response = self.__options(url,headers=headers)
        file_name = os.path.basename(str(upload_file))
        '''
        file_extension = os.path.splitext(str(upload_file))[1]
        if file_extension and len(file_extension) > 1 and file_extension.startswith("."):
            file_extension = file_extension[1:(len(file_extension))]
        file_type = 'image/%s'%(file_extension)
        '''
        file_size = int(os.path.getsize(upload_file))
        file_mimetype = mimetypes.guess_type(upload_file)[0]
       
        mediatype = "pic"
        if not file_mimetype or not file_mimetype.startswith("image"):
            mediatype = "doc"
            
        files = [('filename',("%s"%(file_name),open(upload_file,'rb'),file_mimetype))]
        with open(upload_file,'rb') as fe:
            md5 = hashlib.md5()
            md5.update(fe.read())
            file_md5_digest = md5.hexdigest()
            
        webwx_data_ticket = self.__session.cookies['webwx_data_ticket']
        client_media_id =int(time.time())
        #self.resetdeviceid()
        uploadmediarequest = json.dumps({
            "UploadType":2,
            "BaseRequest": self.__base_request,
            "ClientMediaId":client_media_id,
            "TotalLen":file_size,
            "StartPos":0,
            "DataLen":file_size,
            "MediaType":4,
            "FromUserName":user_from['UserName'],
            "ToUserName":user_to['UserName'],
            "FileMd5": file_md5_digest
        })
        last_modified_date_seconds = os.stat(upload_file).st_mtime
        tup_last=time.localtime(last_modified_date_seconds)
        strftime = time.strftime("%a %b %d %Y %H:%M:%S",tup_last)
        file_last_modified_date= ("%s %s")%(strftime,"GMT+0800")
        data = {
            "id":"WU_FILE_1",
            "name":file_name,
            "type":file_mimetype,
            "lastModifiedDate":file_last_modified_date,
            "size":file_size,
            "mediatype":mediatype,#pic or doc
            "uploadmediarequest":uploadmediarequest,
            "webwx_data_ticket":webwx_data_ticket,
            "pass_ticket":self.__pass_ticket
        }
        response = self.__post(url=url, data=data,headers=headers,files=files)
        return response
    
    '''
            根据MSG_ID下載圖片
    '''
    def webwx_get_msg_img(self,msg_id,media_type="jpg"):
        url = "https://wx.qq.com/cgi-bin/mmwebwx-bin/webwxgetmsgimg" + \
              '?MsgID=%s&skey=%s&fun=download&type=slave' % (
                  msg_id,self.__skey
              )
        data = self.__get(url,stream=True)
        if data:
            image = ('%s/%s.%s'%(self.cache_image_home,msg_id,media_type))
            with open(image, 'wb') as image:
                image.write(data)
        return data
    
    def webwx_create_chatroom(self,member_list):
        '''
        :param member_list[{UserName:"@xxxxxxxx"}]
        '''
        url = "https://wx.qq.com/cgi-bin/mmwebwx-bin/webwxcreatechatroom" + \
              '?r=%s&lang=%s&pass_ticket=%s' %(
                  int(time.time()),self.__lang,self.__pass_ticket
               )
        #self.resetdeviceid()
        data = {
            "BaseRequest": self.__base_request,
            "MemberCount":len(member_list),
            "MemberList":member_list,
            "Topic":""
        }
        response = self.__post_json(url=url,data=data)
        return response
    
    def webwx_update_chatroom(self,params):
        '''
        url:https://wx.qq.com/cgi-bin/mmwebwx-bin/webwxupdatechatroom?fun=modtopic&lang=zh_TW&pass_ticket=%252FNvW1dfkRrPc2wRfVU049j7VFjA8%252BkjlJjLXv7ulI1U%253D
        '''
        '''
        :param params format:{"NewTopic":"xxx","ChatRoomName":"xxx","BaseRequest":"xxxx"}
        '''
        url = "https://wx.qq.com/cgi-bin/mmwebwx-bin/webwxupdatechatroom" + \
              '?fun=modtopic&lang=%s&pass_ticket=%s' %(
                  self.__lang,self.__pass_ticket
               )
        #self.resetdeviceid()
        params["BaseRequest"]= self.__base_request
        response = self.__post_json(url=url,data=params)
        return response
    
    def __get(self, url, data= {},stream=False):
        _headers = {
            'Connection': 'keep-alive',
            'Referer': 'https://wx.qq.com/',
            'Accept-Language': 'zh-TW,zh-HK;q=0.8,en-US;q=0.5,en;q=0.3',
            'User-Agent': self.__user_agent
        }

        while True:
            response = self.__session.get(url=url, data=data, headers=_headers)
            #self.cookies = data.coookies
            if stream:
                data = response.content
            else:
                response.encoding = 'utf-8'
                data = response.text
                logging.debug(url)
                logging.debug(data)
            response.close()
            return data
            '''
            try:
            except (KeyboardInterrupt, SystemExit):
                print("KeyboardInterrupt SystemExit")
            except:
                print("except")
            '''

    def __post(self, url, data, headers={}, stream=False,files=None):
        _headers = {
            'Connection': 'keep-alive',
            'Referer': 'https://wx.qq.com/',
            'User-Agent': self.__user_agent
        }
        #'Content-Type': 'application/json; charset=UTF-8',

        for (key,value) in headers.items():
            _headers[key]=value

        while True:
            try:
                response = self.__session.post(url=url, data=data, headers=_headers,files=files)
                
                if stream:
                    data = response.content
                else:
                    response.encoding='utf-8'
                    data = response.text
                response.close()
                return data
            except KeyboardInterrupt as e:
                logging.error(e)
                raise
                return False
            except SystemExit as e:
                logging.error(e)
                raise
                return False
            except Exception as e:
                logging.error(e)
                return False

    def __post_json(self, url, data, headers={}):
        _headers = {
            'Connection': 'keep-alive',
            'Referer': 'https://wx.qq.com/',
            'Accept-Language': 'zh-TW,zh-HK;q=0.8,en-US;q=0.5,en;q=0.3',
            'User-Agent': self.__user_agent,
            "Content-Type": "application/json; charset=UTF-8"
        }

        for (key,value) in headers.items():
            _headers[key]=value

        while True:
            try:
                response = self.__session.post(url=url, data=json.dumps(data, ensure_ascii=False).encode('utf8'), headers=_headers)
                response.encoding='utf-8'
                response_text = response.text
                logging.info(url)
                logging.info(response_text)
                response.close()
                return response_text
            except (KeyboardInterrupt, SystemExit) as e:
                logging.error(e)
                raise
                return False
            except Exception as e:
                logging.error(e)
                return False
    
    def __options(self, url, data=None, headers={}):
        _headers = {
            'Connection': 'keep-alive',
            'User-Agent': self.__user_agent
        }

        for (key,value) in headers.items():
            _headers[key]=value
        try:
            response = self.__session.options(url=url,headers=_headers)
            response.encoding='utf-8'
            data = response.text
            response.close()
            return data
        except (KeyboardInterrupt, SystemExit) as e:
            logging.error(e)
            raise
            return None
        except Exception as e:
            logging.error(e)
            return None


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
    api.webwx_status_notify()
    api.webwx_get_contact()
    api.sync_check()
    #da = wechatweb.webwx_sync()





