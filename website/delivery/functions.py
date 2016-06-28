#coding=utf-8

from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.conf import settings

from sendfile import sendfile
from delivery.models import *
import hashlib
import random
import os

def genSMSCode(length = 4):
    r_starts = "1" + "0"*(length -1)
    r_ends = "9"*length
    code = random.randint(int(r_starts),int(r_ends))
    return code

def getFile(request,file_name):
    '''
    sendfile 返回数据信息给nginx
    '''
    file_path = os.path.join(settings.MEDIA_ROOT,file_name)
    return sendfile(request,file_path,attachment=True,attachment_filename=file_name)

def send_sms(phone_num):
    '''
    '''
    code = genSMSCode()
    sms = SMS(
        code = code,
        phone_num = phone_num
        )
    status = sms.send()
    return (status,code)

def send_email(email,report_file_name):
    '''
    一次性动作，不记录状态
    '''
    email_subject = "Report for xx"
    email_body = render_to_string("message/report.txt",{})
    email = EmailMessage(
        email_subject,
        email_body,
        settings.EMAIL_HOST_USER,
        [email,],
    )
    email.attach_file(report_file_name)
    email.send()

def setSession(request,userID):
    Sessionkey = "user_session_key"
    if Sessionkey in request.session:
        if request.session[Sessionkey] != userID:
            request.session.flush()
    request.session[Sessionkey] = userID

def getSession(request):
    Sessionkey = "user_session_key"
    if Sessionkey not in request.session:
        return False
    userID = request.session[Sessionkey]
    try:
        u = User.objects.get(userID = userID)
    except Exception,ex:
        return False
    else:
        return u

def delSession(request):
    Sessionkey = "user_session_key"
    if getSession(request):
        del request.session[Sessionkey]
