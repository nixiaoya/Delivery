#coding=utf-8
from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.template.loader import get_template

from delivery.functions import *
from delivery.models import *

import re

class MyException(Exception):
    pass


def auth_required(func):
    def _auth_required(request):
        if not getSession(request):
            # context = {
            #     "status":1,
            #     "msg":u"手机号未验证"
            #     }
            # return JsonResponse(context)
            return HttpResponse("未授权的操作")
        else:
            return func(request)
    return _auth_required


def Home(request):
    context = {}
    template = get_template("main/home.html")
    html = template.render(context,request)
    return HttpResponse(html)

def sendSMS(request):
    '''
    请求验证码
    '''
    phone_num = request.POST.get("phone_num","").strip()
    msg = "验证短信发送成功"
    status_code = 0

    re1 = re.compile(r'^\d{11}$')
    if re1.match(phone_num):
        (send_success,sms_code) = send_sms(phone_num)
        if send_success:
            if User.objects.filter(phoneNum = phone_num).exists():
                u = User.objects.get(phoneNum = phone_num)
            else:
                u = User(
                    phoneNum = phone_num,
                    )
            u.init_user(str(sms_code))
            u.save()
        else:
            status_code = 2
            msg = u"验证短信发送失败"
    else:
        status_code = 1
        msg = u"非法的手机号码"
    context = {
        "status":status_code,
        "msg":msg
    }

    return JsonResponse(context)

def postSMS(request):
    '''
    验证手机号
    '''
    sms_code = request.POST.get("sms_code","").strip()
    phone_num = request.POST.get("phone_num","").strip()
    status_code = 0
    msg = u"手机号验证成功"

    if User.objects.filter(phoneNum = phone_num, smsCode = sms_code).count() == 1:
        u = User.objects.filter(phoneNum = phone_num, smsCode = sms_code)[0]
        if not u.codeExpired():
            setSession(request, u.userID)
        else:
            status_code = 2 
            msg = u"验证码已过期"
    else:
        status_code = 1
        msg = u"验证码不匹配"
    context = {
        "status":status_code,
        "msg":msg
    }
    return JsonResponse(context)

@auth_required
def sendMail(request):
    '''
    发送报告
    '''
    email = request.POST.get("email","").strip()
    msg = u"邮件已发送。若未收到邮件，请检查邮箱是否填写正确"
    status_code = 0

    u =  getSession(request)
    report_file = u.getReportFile()

    if email:
        re1 = re.compile(r'^[a-zA-Z0-9_]{3,15}@[a-zA-Z0-9]{2,10}\.[a-z]{2,5}$')
        if re1.match(email):
            try:
                send_email(email,report_file)
            except Exception,ex:
                msg= u"邮件发送失败"
                status_code = 2
        else:
            msg = u"非法的邮箱地址"
            status_code = 1
        report_file = ""
    else:
        report_file = "download/?f=%s" % u.report
    context = {
        "status":status_code,
        "msg":msg,
        "reportFile":report_file,
    }
    return JsonResponse(context)

@auth_required
def Download(request):
    file_name = request.GET.get("f","").strip()
    # 防止其他人的session获取文件
    user_id = getSession(request)
    if file_name and User.objects.filter(userID = user_id, report = file_name).count() == 1:
        return getFile(request,file_name)
    else:
        return HttpResponse(u"未授权的文件下载")
