# -*- coding: utf-8 -*-
"""ld URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import include, url
# from django.contrib import admin

urlpatterns = [
    # url(r'^admin/', include(admin.site.urls)),

    #登录
    url(r'^$', 'login.views.login_index', name='登录页面'),
    url(r'^login/$', 'login.views.login_index', name='登录页面'),
    url(r'^logout/$', 'login.views.logout', name='退出页面'),
    # url(r'^passwd/$', 'login.views.passwd', name='密码修改'),

    #未考勤
    url(r'^no_attendance/', include('no_attendance.urls')),
]
