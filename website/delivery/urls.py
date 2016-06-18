from django.conf.urls import *
from delivery import views

urlpatterns = [
    url(r'^sendSMS/$', views.sendSMS),
    url(r'^postSMS/$', views.postSMS),
    url(r'^sendMail/$', views.sendMail),
    url(r'^download/$', views.Download),
    url(r'^$', views.Home)
]

