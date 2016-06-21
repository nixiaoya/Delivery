from django.contrib import admin
from . import models

class User_Admin(admin.ModelAdmin):
    search_fields = ("phoneNum",)
    list_display = ("phoneNum","smsCode","userID","report")
admin.site.register(models.User,User_Admin)

class SMSLog_Admin(admin.ModelAdmin):
    search_fields = ("phoneNum",)
    list_display = ("jobStart","phoneNum","content","jobSuccess","log")
admin.site.register(models.SMSLog,SMSLog_Admin)

