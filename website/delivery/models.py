#coding=utf-8
from __future__ import unicode_literals

from django.db import models
from django.conf import settings
from django.utils import timezone

from pyDes import *
import hashlib
import base64
import datetime
import time
import json
import urllib2
import urllib
import socket
import os

class MyExcept(Exception):
    pass

class User(models.Model):
    '''
    用户信息
    '''
    phoneNum = models.CharField(max_length=64, help_text=u'电话号码')
    smsCode = models.CharField(max_length=64, blank=True, help_text=u"短信验证码")
    userID = models.CharField(max_length=64, db_index=True, help_text=u"用户临时编码")
    report = models.CharField(max_length=64, blank=True, help_text=u'报告名称')
    expires=  models.DateTimeField(help_text=u'报告名称')
    
    def genSalt(self):
        m1 = hashlib.md5()
        m1.update(str(time.time()) + self.phoneNum)
        return m1.hexdigest()[:10]

    def encrypt(self,str_):
        s1 = hashlib.sha256()
        s1.update(str_)
        return s1.hexdigest()

    def init_user(self, code):
        '''
        初始化用户的临时属性：临时ID，验证码，验证码的过期时间
        '''
	self.report = "Report.pdf"
        self.userID = self.genSalt()
        self.smsCode = code 
        self.expires = (datetime.datetime.now() + datetime.timedelta(seconds = settings.SMS_EXPIRES))

    def codeExpired(self):
        current_time = timezone.now()
        if current_time > self.expires:
            return True
        else:
            return False

    def getReportFile(self):
        return os.path.join(settings.MEDIA_ROOT,self.report)

    def __unicode__(self):
        return self.userID
        
class SMSLog(models.Model):
    phoneNum = models.CharField(max_length=64, blank=True)
    content = models.CharField(max_length=128, blank=True)
    sendTime = models.CharField(max_length=64, blank=True)
    action = models.CharField(max_length=64, blank=True)
    stamp = models.CharField(max_length=64, blank=True)
    extno = models.CharField(max_length=64, blank=True)
    respStatus = models.CharField(max_length=64, blank=True)
    respMsg = models.CharField(max_length=64, blank=True)
    respRemain = models.CharField(max_length=64, blank=True)
    respTaskID = models.CharField(max_length=64, blank=True)
    respSuccess = models.CharField(max_length=64, blank=True)
    jobStart = models.DateTimeField(auto_now_add=True)
    respErrors = models.CharField(max_length=128, blank=True)
    jobStart = models.DateTimeField(auto_now_add=True)
    log = models.TextField(blank=True)

    def init_request(self,data):
        if data.has_key("content"):
            self.content = data["content"]
        if data.has_key("mobile"):
            self.phoneNum = data["mobile"]
        if data.has_key("Mobile"):
            self.phoneNum = data["Mobile"]
        if data.has_key("sendTime"):
            self.sendTime = data["sendTime"]
        if data.has_key("action"):
            self.action = data["action"]
        if data.has_key("extno"):
            self.extno = data["extno"]
        if data.has_key("Text"):
            self.content = data["Text"]
        if data.has_key("SendTime"):
            self.sendTime = data["SendTime"]
        if data.has_key("Stamp"):
            self.stamp = data["Stamp"]
        if data.has_key("Ext"):
            self.extno = data["Ext"]
        self.save()

    def init_response(self,data):
        if type(data) == dict:
            if data.has_key("returnstatus") and data["returnstatus"]:
                self.respStatus = data["returnstatus"]
            if data.has_key("message") and data["message"]:
                self.respMsg = data["message"]
            if data.has_key("remainpoint") and data["remainpoint"]:
                self.respRemain = data["remainpoint"]
            if data.has_key("tastID") and data["tastID"]:
                self.respTaskID = data["tastID"]
            if data.has_key("successCounts") and data["successCounts"]:
                self.respSuccess = data["successCounts"]
            if data.has_key("StatusCode") and data["StatusCode"]:
                self.respStatus = data["StatusCode"]
            if data.has_key("Description") and data["Description"]:
                self.respMsg = data["Description"]
            if data.has_key("Amount") and data["Amount"]:
                self.respRemain = data["Amount"]
            if data.has_key("MsgId") and data["MsgId"]:
                self.respTaskID = data["MsgId"]
            if data.has_key("SuccessCounts") and data["SuccessCounts"]:
                self.respSuccess = data["SuccessCounts"]
            if data.has_key("Errors") and data["Errors"]:
                self.respErrors = data["Errors"]
            self.save()

    def errorlog(self,error):
        self.log += error + "\n"
        self.save()

    def __unicode__(self):
        return self.phoneNum + self.content

## none django models

class DES(object):
    def __init__(self,key):
        self.key = str(key)

    def encrypt(self,data):
        while len(self.key) < 8:
            self.key += "\x00"
        KEY = str(self.key[:8])
        IV = KEY
        k = des(KEY, CBC, IV, pad=None, padmode=PAD_PKCS5)
        d = k.encrypt(data)
        d = base64.encodestring(d).replace('\n','')
        return d

    def decrypt(sellf,data):
        pass

class SMS(object):
    def __init__(self,code,phone_num,extno="",sendTime="",action="send"):
        self.smsAPI = settings.SMS_HOST
        self.smsEnAPI= settings.SMS_EN_HOST
        self.smsAccount = settings.SMS_ACCOUNT
        self.smsPassword = settings.SMS_PASSWORD
        self.content = '手机验证码为: ' + \
                        str(code) + \
                        '【' + settings.SERVICE_FROM + '】'
        self.phone_num = phone_num
        self.extno = extno
        self.sendTime = sendTime
        self.action = action
        self.log = SMSLog()

    def e1(self,stamp):
        m5 = hashlib.md5()
        m5.update(self.smsPassword + stamp)
        return m5.hexdigest().upper()

    def send_non_encrypt(self):
        '''
        明文验证
        '''
        req_data = {
            "account":self.smsAccount,
            "password":self.smsPassword,
            "mobile":self.phone_num,
            "content":self.content.encode("utf-8"),
            "sendTime":self.sendTime,
            "action":self.action,
            "extno":self.extno
        }
        self.log.init_request(req_data)

        url = self.smsAPI
        header = {}
        req = urllib2.Request(url,urllib.urlencode(req_data),header)

        try:
            sms_resp = urllib2.urlopen(req, timeout=5)
        except urllib2.HTTPError as e:
            self.log.errorlog("HttpError: code=>%s reason=>%s" % (e.code,e.reason))
            return False
        except urllib2.URLError as e:     
            self.log.errorlog("URLError: %s" % e.reason)
            return False
        except socket.timeout as e:
            self.log.errorlog("Socket timeout:%s" % e)
            return False
        else:
            try:
                resp_data = json.loads(sms_resp.read())
            except ValueError as e:
                self.log.errorlog("ValueError: %s" % e)
                return False
            else:
                self.log.init_response(resp_data)

                if resp_data["returnstatus"] == "Success":
                    return True
                else:
                    return False

    def send_encrypt(self):
        '''
        密文验证
        '''
        stamp = datetime.datetime.strftime(datetime.datetime.now(),"%m%d%H%M%S")
       
        secret = self.e1(stamp)
        req_data = {
            "userid":"",
            "UserName":self.smsAccount,
            "Stamp":stamp,
            "Secret":secret,
            "Mobile":self.phone_num,
            "Text":self.content,
            "Ext":self.extno,
            "SendTime":self.sendTime
        }
        self.log.init_request(req_data)

        req_str = json.dumps(req_data)
        des = DES(self.smsPassword)
        encrypt_req_str = des.encrypt(req_str)

        encrypt_req_data = {
            "Text64":encrypt_req_str
        }

        url = self.smsEnAPI
        header = {}
        req = urllib2.Request(url,urllib.urlencode(encrypt_req_data),header)

        try:
            sms_resp = urllib2.urlopen(req, timeout=5)
        except urllib2.HTTPError as e:
            self.log.errorlog("HttpError: code=>%s reason=>%s" % (e.code,e.reason))
            return False
        except urllib2.URLError as e:     
            self.log.errorlog("URLError: %s" % e.reason)
            return False
        except socket.timeout as e:
            self.log.errorlog("Socket timeout:%s" % e)
            return False
        else:
            try:
                resp_data = json.loads(sms_resp.read())
            except ValueError as e:
                self.log.errorlog("ValueError: %s" % e)
                raise MyException(e)
                return False
            else:
                self.log.init_response(resp_data)

                if resp_data["StatusCode"] == "1":
                    return True
                else:
                    return False
    def send(self, encrypt = True):
        if encrypt == True:
            return self.send_encrypt()
        else:
            return self.send_non_encrypt()
