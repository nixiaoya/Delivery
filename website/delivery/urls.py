from django.conf.urls import *
from delivery import views

handler404 = 'delivery.views.error404'
handler500 = 'delivery.views.error500'

urlpatterns = [
    url(r'^sendSMS/$', views.sendSMS),
    url(r'^postSMS/$', views.postSMS),
    url(r'^sendMail/$', views.sendMail),
    url(r'^download/$', views.Download),
    url(r'^$', views.Home, name='home')
]

